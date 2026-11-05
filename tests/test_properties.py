"""Property-style tests: identities that must hold for ANY valid input set."""
import math
import random

import numpy as np
import numpy_financial as npf
import pytest

from feasibility import ProjectInputs, build_cashflow, appraise
from feasibility.metrics import npv, irr, monthly_rate_from_annual


def random_inputs(seed: int) -> ProjectInputs:
    r = random.Random(seed)
    c_start = r.randint(1, 8)
    c_end = c_start + r.randint(0, 30)
    s_start = r.randint(1, 15)
    s_end = s_start + r.randint(0, 30)
    ap_start = r.randint(1, 4)
    return ProjectInputs(
        horizon_months=r.randint(12, 48),
        land_cost_cr=r.uniform(0, 60), land_month=r.randint(1, 6),
        approval_cost_cr=r.uniform(0, 8), approval_start=ap_start, approval_end=ap_start + r.randint(0, 6),
        saleable_area_sqft=r.uniform(20_000, 500_000), construction_cost_per_sqft=r.uniform(1500, 6000),
        construction_start=c_start, construction_end=c_end,
        selling_price_per_sqft=r.uniform(3000, 15000), sales_start=s_start, sales_end=s_end,
        booking_pct=r.uniform(0, 1), instalment_months=r.randint(0, 18), marketing_pct=r.uniform(0, 0.05),
        debt_pct_of_costs=r.uniform(0, 1), interest_rate=r.uniform(0, 0.2), repayment_sweep_pct=r.uniform(0, 1),
        tax_rate=r.uniform(0, 0.4), discount_rate=r.uniform(0.05, 0.3),
    )


SEEDS = list(range(200))


@pytest.mark.parametrize("seed", SEEDS)
def test_accounting_identities(seed):
    inp = random_inputs(seed)
    df = build_cashflow(inp)
    tol = 1e-9 * max(1.0, inp.gross_revenue_cr)
    # spend lands fully
    assert abs(-df["land"].sum() - inp.land_cost_cr) < tol
    assert abs(-df["approvals"].sum() - inp.approval_cost_cr) < tol
    assert abs(-df["construction"].sum() - inp.construction_cost_cr) < tol
    # all sales collected within horizon
    assert abs(df["sales_booked"].sum() - inp.gross_revenue_cr) < tol
    assert abs(df["collections"].sum() - inp.gross_revenue_cr) < tol
    # debt closes at zero, repayments = drawdowns
    assert abs(df["debt_closing"].iloc[-1]) < tol
    assert abs(df["drawdown"].sum() + df["repayment"].sum()) < tol
    assert abs(df["drawdown"].sum() - inp.debt_pct_of_costs * (inp.land_cost_cr + inp.approval_cost_cr + inp.construction_cost_cr)) < tol
    # balances never negative, interest never positive, drawdown never negative
    assert (df["debt_closing"] >= -tol).all()
    assert (df["interest"] <= tol).all()
    assert (df["drawdown"] >= -tol).all()
    # equity = project + debt flows
    assert np.allclose(df["project_cf"] + df["drawdown"] + df["interest"] + df["repayment"], df["equity_cf"])
    # monthly interest = opening * rate/12
    assert np.allclose(-df["interest"], df["debt_opening"] * inp.interest_rate / 12)
    # tax only in last month, non-negative
    assert (df["tax"].iloc[:-1] == 0).all() and df["tax"].iloc[-1] <= 0
    # horizon covers everything
    assert len(df) == inp.effective_horizon >= max(inp.sales_end + inp.instalment_months, inp.construction_end)


@pytest.mark.parametrize("seed", SEEDS[:60])
def test_npv_irr_against_numpy_financial(seed):
    inp = random_inputs(seed)
    df = build_cashflow(inp)
    eq = df["equity_cf"].to_numpy()
    rm = monthly_rate_from_annual(inp.discount_rate)
    # numpy_financial.npv treats the first flow as t=0, so shift by one period
    assert math.isclose(npv(rm, eq), npf.npv(rm, np.concatenate([[0.0], eq])), rel_tol=1e-10, abs_tol=1e-9)
    ours = irr(eq)
    theirs = npf.irr(eq)
    if ours is not None and theirs is not None and not np.isnan(theirs):
        # both are roots; if they differ both must still give ~0 NPV
        assert abs(npv(ours, eq)) < 1e-6
        assert abs(npv(theirs, eq)) < 1e-4


@pytest.mark.parametrize("seed", SEEDS[:60])
def test_irr_is_a_root_and_breakeven_is_consistent(seed):
    inp = random_inputs(seed)
    a = appraise(inp)
    df = build_cashflow(inp)
    if a.irr_equity_annual is not None:
        rm = (1 + a.irr_equity_annual) ** (1 / 12) - 1
        assert abs(npv(rm, df["equity_cf"].to_numpy())) < 1e-6
    if a.breakeven_price_npv_zero is not None:
        be = appraise(inp.with_changes(selling_price_per_sqft=a.breakeven_price_npv_zero))
        assert abs(be.npv_equity_cr) < 1e-4
    if a.breakeven_price_profit_zero is not None:
        be = appraise(inp.with_changes(selling_price_per_sqft=a.breakeven_price_profit_zero))
        assert abs(be.pre_tax_profit_cr) < 1e-4


@pytest.mark.parametrize("seed", SEEDS[:40])
def test_monotonicity(seed):
    inp = random_inputs(seed)
    base = appraise(inp).npv_equity_cr
    assert appraise(inp.with_changes(selling_price_per_sqft=inp.selling_price_per_sqft * 1.1)).npv_equity_cr >= base - 1e-9
    assert appraise(inp.with_changes(construction_cost_per_sqft=inp.construction_cost_per_sqft * 1.1)).npv_equity_cr <= base + 1e-9
    assert appraise(inp.with_changes(land_cost_cr=inp.land_cost_cr * 1.1 + 0.1)).npv_equity_cr <= base + 1e-9
    # NPV falls with the discount rate only for conventional cash flows: outflows first,
    # then inflows, with a single sign change. Reversed or multi-sign-change patterns can
    # legitimately show NPV rising with the rate, and so can a loss-making project (NPV < 0 at
    # every rate: a higher rate shrinks the loss). Correct finance, not a model bug.
    eq = build_cashflow(inp)["equity_cf"].to_numpy()
    signs = np.sign(eq[np.abs(eq) > 1e-12])
    if base > 0 and signs[0] < 0 and int((signs[:-1] * signs[1:] < 0).sum()) == 1:
        assert appraise(inp.with_changes(discount_rate=inp.discount_rate + 0.02)).npv_equity_cr <= base + 1e-9
    # a cheaper loan can never hurt equity
    assert appraise(inp.with_changes(interest_rate=max(0.0, inp.interest_rate - 0.02))).npv_equity_cr >= base - 1e-9


def test_no_debt_equity_equals_project():
    for seed in range(20):
        inp = random_inputs(seed).with_changes(debt_pct_of_costs=0.0)
        a = appraise(inp)
        assert math.isclose(a.npv_equity_cr, a.npv_project_cr, rel_tol=1e-12, abs_tol=1e-12)
        if a.irr_equity_annual is not None:
            assert math.isclose(a.irr_equity_annual, a.irr_project_annual, rel_tol=1e-9, abs_tol=1e-9)
