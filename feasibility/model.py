"""Monthly cash flow engine.

Every line below is deliberately simple enough to reproduce in a plain
spreadsheet. The benchmark workbook in benchmark/ implements the same logic
with Excel formulas so the two can be compared independently.

Sign convention: inflows positive, outflows negative, in INR crore.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .inputs import ProjectInputs


def smoothstep_weights(start: int, end: int) -> dict[int, float]:
    """S-curve spend weights for months start..end (inclusive).

    Cumulative share at the end of the k-th month of a D-month window is
    S(x) = 3x^2 - 2x^3 with x = k / D. The monthly weight is the difference of
    consecutive cumulative shares. Weights sum to exactly 1.
    """
    duration = end - start + 1
    weights = {}
    prev = 0.0
    for k in range(1, duration + 1):
        x = k / duration
        cum = 3 * x**2 - 2 * x**3
        weights[start + k - 1] = cum - prev
        prev = cum
    return weights


def even_weights(start: int, end: int) -> dict[int, float]:
    duration = end - start + 1
    return {m: 1.0 / duration for m in range(start, end + 1)}


def build_cashflow(inp: ProjectInputs) -> pd.DataFrame:
    """Return a DataFrame with one row per month (index = month number)."""
    problems = inp.validate()
    if problems:
        raise ValueError("; ".join(problems))

    n = inp.effective_horizon
    months = np.arange(1, n + 1)
    df = pd.DataFrame(index=pd.Index(months, name="month"))

    # ---- Outflows: land, approvals, construction ---------------------------
    land = np.zeros(n)
    land[inp.land_month - 1] = inp.land_cost_cr

    approvals = np.zeros(n)
    for m, w in even_weights(inp.approval_start, inp.approval_end).items():
        approvals[m - 1] = inp.approval_cost_cr * w

    construction = np.zeros(n)
    for m, w in smoothstep_weights(inp.construction_start, inp.construction_end).items():
        construction[m - 1] = inp.construction_cost_cr * w

    # ---- Sales and collections -------------------------------------------
    sales_booked = np.zeros(n)  # value of area sold in the month
    for m, w in even_weights(inp.sales_start, inp.sales_end).items():
        sales_booked[m - 1] = inp.gross_revenue_cr * w

    # Collection profile: booking_pct in month of sale, balance spread evenly
    # over the next `instalment_months` months.
    collections = np.zeros(n)
    k = inp.instalment_months
    for t in range(n):
        s = sales_booked[t]
        if s == 0:
            continue
        collections[t] += s * inp.booking_pct
        if k > 0:
            per_inst = s * (1 - inp.booking_pct) / k
            for j in range(1, k + 1):
                if t + j < n:
                    collections[t + j] += per_inst
        else:
            collections[t] += s * (1 - inp.booking_pct)

    marketing = collections * inp.marketing_pct

    # ---- Debt schedule (sequential, month by month) ----------------------
    monthly_rate = inp.interest_rate / 12
    opening = np.zeros(n)
    drawdown = (land + approvals + construction) * inp.debt_pct_of_costs
    interest = np.zeros(n)
    repayment = np.zeros(n)
    closing = np.zeros(n)
    bal = 0.0
    for t in range(n):
        opening[t] = bal
        interest[t] = bal * monthly_rate
        available = bal + drawdown[t]
        rep = min(available, collections[t] * inp.repayment_sweep_pct)
        if t == n - 1:
            rep = available  # bullet repayment of any residual balance in the final month
        repayment[t] = rep
        bal = available - rep
        closing[t] = bal

    # ---- Tax (on accounting profit, paid in the final month) --------------
    total_revenue = sales_booked.sum()
    total_cost = land.sum() + approvals.sum() + construction.sum() + marketing.sum() + interest.sum()
    pre_tax_profit = total_revenue - total_cost
    tax = np.zeros(n)
    tax[-1] = max(0.0, pre_tax_profit * inp.tax_rate)

    # ---- Assemble ---------------------------------------------------------
    df["land"] = -land
    df["approvals"] = -approvals
    df["construction"] = -construction
    df["marketing"] = -marketing
    df["sales_booked"] = sales_booked
    df["collections"] = collections
    df["tax"] = -tax
    df["project_cf"] = (
        df["collections"] + df["land"] + df["approvals"] + df["construction"] + df["marketing"] + df["tax"]
    )
    df["debt_opening"] = opening
    df["drawdown"] = drawdown
    df["interest"] = -interest
    df["repayment"] = -repayment
    df["debt_closing"] = closing
    df["equity_cf"] = df["project_cf"] + df["drawdown"] + df["interest"] + df["repayment"]
    df["cum_project_cf"] = df["project_cf"].cumsum()
    df["cum_equity_cf"] = df["equity_cf"].cumsum()
    df["cum_outflow"] = (df["land"] + df["approvals"] + df["construction"] + df["marketing"]).cumsum()
    df["cum_collections"] = df["collections"].cumsum()
    return df
