"""Appraisal metrics computed from the monthly cash flow table."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import math

import numpy as np
import pandas as pd

from .inputs import ProjectInputs
from .model import build_cashflow


def monthly_rate_from_annual(annual: float) -> float:
    """Effective monthly rate equivalent to an effective annual rate."""
    return (1 + annual) ** (1 / 12) - 1


def npv(rate_m: float, cashflows: np.ndarray) -> float:
    """NPV with the first cash flow discounted one period (end-of-month convention).

    Matches Excel's NPV(rate, range) exactly.
    """
    t = np.arange(1, len(cashflows) + 1)
    return float(np.sum(cashflows / (1 + rate_m) ** t))


def irr(cashflows: np.ndarray, tol: float = 1e-10) -> float | None:
    """Periodic IRR.

    Scans monthly rates from -50% upward to +100% per period for the first sign
    change of NPV, then refines by bisection. Returns None if NPV never
    changes sign (no meaningful IRR).
    """
    cf = np.asarray(cashflows, dtype=float)
    if not (np.any(cf > 0) and np.any(cf < 0)):
        return None
    grid = np.arange(-0.5, 1.0, 0.0025)
    vals = np.array([npv(r, cf) for r in grid])
    sign_change = np.nonzero(np.sign(vals[:-1]) * np.sign(vals[1:]) < 0)[0]
    if len(sign_change) == 0:
        return None
    # take the sign change closest to zero rate (the economically relevant root)
    i = sign_change[np.argmin(np.abs(grid[sign_change]))]
    lo, hi = grid[i], grid[i + 1]
    f_lo = vals[i]
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid, cf)
        if abs(f_mid) < tol or (hi - lo) < 1e-13:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def irr_root_count(cashflows: np.ndarray) -> int:
    """Number of distinct rates in the economically plausible band [-10%, +50%) per
    month (about -72% to +12,900% per year) at which NPV changes sign.

    Roots outside the band (e.g. at -98% per year, which every project with a final
    tax payment has) are ignored. More than one root inside the band means the IRR
    is not unique and should not be used for decisions; NPV at the hurdle rate is
    the reliable measure in that case.
    """
    cf = np.asarray(cashflows, dtype=float)
    if not (np.any(cf > 0) and np.any(cf < 0)):
        return 0
    grid = np.arange(-0.10, 0.50, 0.0025)
    vals = np.array([npv(r, cf) for r in grid])
    return int(np.count_nonzero(np.sign(vals[:-1]) * np.sign(vals[1:]) < 0))


def sign_changes(cashflows: np.ndarray) -> int:
    cf = np.asarray(cashflows, dtype=float)
    signs = np.sign(cf[np.abs(cf) > 1e-12])
    return int(np.count_nonzero(signs[:-1] * signs[1:] < 0)) if len(signs) > 1 else 0


def annualise(rate_m: float | None) -> float | None:
    return None if rate_m is None else (1 + rate_m) ** 12 - 1


def payback_month(cashflows: np.ndarray) -> int | None:
    """First month in which cumulative cash flow becomes >= 0 after having been negative."""
    cum = np.cumsum(cashflows)
    if not np.any(cum < 0):
        return None
    neg_seen = False
    for i, c in enumerate(cum):
        if c < 0:
            neg_seen = True
        elif neg_seen and c >= 0:
            return i + 1
    return None


@dataclass
class Appraisal:
    # headline
    npv_equity_cr: float
    irr_equity_annual: float | None
    irr_project_annual: float | None
    irr_equity_roots: int                       # >1 means the equity IRR is not unique
    irr_project_roots: int
    equity_sign_changes: int
    irr_unreliable: bool                        # IRR not unique, or IRR vs hurdle disagrees with NPV sign
    npv_project_cr: float
    payback_equity_months: int | None
    discounted_payback_equity_months: int | None
    profit_on_cost_pre_tax: float
    profit_on_cost_post_tax: float
    breakeven_price_npv_zero: float | None      # price at which equity NPV = 0
    breakeven_price_profit_zero: float | None   # price at which pre-tax profit = 0
    # totals
    gross_revenue_cr: float
    total_development_cost_cr: float            # land + approvals + construction + marketing + interest
    land_cr: float
    approvals_cr: float
    construction_cr: float
    marketing_cr: float
    interest_cr: float
    tax_cr: float
    pre_tax_profit_cr: float
    post_tax_profit_cr: float
    peak_debt_cr: float
    peak_equity_requirement_cr: float           # most negative cumulative equity cash flow
    peak_equity_month: int
    debt_fully_repaid_month: int | None
    effective_horizon: int
    discount_rate_monthly: float

    def to_dict(self):
        return asdict(self)


def appraise(inp: ProjectInputs, df: pd.DataFrame | None = None, compute_breakeven: bool = True) -> Appraisal:
    """Full appraisal. Set compute_breakeven=False inside loops (sensitivity, scenarios):
    the two bisection solves cost ~300 ms, the rest of the appraisal ~10 ms."""
    if df is None:
        df = build_cashflow(inp)
    rm = monthly_rate_from_annual(inp.discount_rate)
    eq = df["equity_cf"].to_numpy()
    pj = df["project_cf"].to_numpy()

    land = -df["land"].sum()
    approvals = -df["approvals"].sum()
    construction = -df["construction"].sum()
    marketing = -df["marketing"].sum()
    interest = -df["interest"].sum()
    tax = -df["tax"].sum()
    revenue = df["sales_booked"].sum()
    tdc = land + approvals + construction + marketing + interest
    pre_tax = revenue - tdc
    post_tax = pre_tax - tax

    # discounted payback
    t = np.arange(1, len(eq) + 1)
    disc_eq = eq / (1 + rm) ** t

    cum_eq = df["cum_equity_cf"].to_numpy()
    peak_idx = int(np.argmin(cum_eq))

    repaid = None
    closing = df["debt_closing"].to_numpy()
    drawn = df["drawdown"].to_numpy()
    if drawn.sum() > 0:
        last_draw = int(np.max(np.nonzero(drawn)[0]))
        for i in range(last_draw, len(closing)):
            if closing[i] <= 1e-9:
                repaid = i + 1
                break

    npv_eq = npv(rm, eq)
    irr_eq = annualise(irr(eq))
    roots_eq = irr_root_count(eq)
    inconsistent = irr_eq is not None and ((irr_eq > inp.discount_rate) != (npv_eq > 0))

    return Appraisal(
        npv_equity_cr=npv_eq,
        irr_equity_annual=irr_eq,
        irr_project_annual=annualise(irr(pj)),
        irr_equity_roots=roots_eq,
        irr_unreliable=(roots_eq > 1 or inconsistent),
        irr_project_roots=irr_root_count(pj),
        equity_sign_changes=sign_changes(eq),
        npv_project_cr=npv(rm, pj),
        payback_equity_months=payback_month(eq),
        discounted_payback_equity_months=payback_month(disc_eq),
        profit_on_cost_pre_tax=pre_tax / tdc if tdc else float("nan"),
        profit_on_cost_post_tax=post_tax / tdc if tdc else float("nan"),
        breakeven_price_npv_zero=breakeven_price(inp, target="npv") if compute_breakeven else None,
        breakeven_price_profit_zero=breakeven_price(inp, target="profit") if compute_breakeven else None,
        gross_revenue_cr=revenue,
        total_development_cost_cr=tdc,
        land_cr=land,
        approvals_cr=approvals,
        construction_cr=construction,
        marketing_cr=marketing,
        interest_cr=interest,
        tax_cr=tax,
        pre_tax_profit_cr=pre_tax,
        post_tax_profit_cr=post_tax,
        peak_debt_cr=float(df["debt_closing"].max()),
        peak_equity_requirement_cr=float(-cum_eq[peak_idx]),
        peak_equity_month=peak_idx + 1,
        debt_fully_repaid_month=repaid,
        effective_horizon=len(df),
        discount_rate_monthly=rm,
    )


def _objective(inp: ProjectInputs, price: float, target: str) -> float:
    trial = inp.with_changes(selling_price_per_sqft=price)
    df = build_cashflow(trial)
    if target == "npv":
        rm = monthly_rate_from_annual(inp.discount_rate)
        return npv(rm, df["equity_cf"].to_numpy())
    # pre-tax profit
    revenue = df["sales_booked"].sum()
    cost = -(df["land"].sum() + df["approvals"].sum() + df["construction"].sum()
             + df["marketing"].sum() + df["interest"].sum())
    return revenue - cost


def breakeven_price(inp: ProjectInputs, target: str = "npv") -> float | None:
    """Selling price (per sq ft) at which equity NPV = 0 (target='npv') or pre-tax profit = 0."""
    lo, hi = 1.0, max(inp.selling_price_per_sqft * 4, 1000.0)
    f_lo, f_hi = _objective(inp, lo, target), _objective(inp, hi, target)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = _objective(inp, mid, target)
        if abs(f_mid) < 1e-9 or (hi - lo) < 1e-6:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2
