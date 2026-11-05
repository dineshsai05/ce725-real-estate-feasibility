import math
import numpy as np
import pytest

from feasibility import BASE_CASE, build_cashflow, appraise
from feasibility.metrics import npv, irr, annualise, monthly_rate_from_annual, payback_month
from feasibility.model import smoothstep_weights, even_weights


def test_npv_matches_hand_calculation():
    # -100 now-ish (end of period 1), +60, +60 at 10%: Excel NPV convention
    cf = np.array([-100.0, 60.0, 60.0])
    expected = -100 / 1.1 + 60 / 1.1**2 + 60 / 1.1**3
    assert math.isclose(npv(0.10, cf), expected, rel_tol=1e-12)


def test_irr_simple():
    cf = np.array([-100.0, 110.0])
    assert math.isclose(irr(cf), 0.10, abs_tol=1e-8)


def test_irr_none_when_all_positive():
    assert irr(np.array([1.0, 2.0])) is None


def test_annualise_roundtrip():
    rm = monthly_rate_from_annual(0.15)
    assert math.isclose(annualise(rm), 0.15, rel_tol=1e-12)


def test_payback():
    assert payback_month(np.array([-10, 4, 4, 4])) == 4
    assert payback_month(np.array([-10, 4, 4])) is None


def test_weights_sum_to_one():
    assert math.isclose(sum(smoothstep_weights(4, 30).values()), 1.0, abs_tol=1e-12)
    assert math.isclose(sum(even_weights(7, 30).values()), 1.0, abs_tol=1e-12)
    assert len(smoothstep_weights(5, 5)) == 1 and smoothstep_weights(5, 5)[5] == 1.0


def test_base_case_identities():
    inp = BASE_CASE
    df = build_cashflow(inp)
    # all spend lands in the table
    assert math.isclose(-df["land"].sum(), inp.land_cost_cr)
    assert math.isclose(-df["approvals"].sum(), inp.approval_cost_cr)
    assert math.isclose(-df["construction"].sum(), inp.construction_cost_cr)
    # every rupee sold is collected within the horizon
    assert math.isclose(df["sales_booked"].sum(), inp.gross_revenue_cr)
    assert math.isclose(df["collections"].sum(), inp.gross_revenue_cr)
    # loan fully repaid, drawdown equals debt share of funded costs
    assert abs(df["debt_closing"].iloc[-1]) < 1e-9
    assert math.isclose(df["drawdown"].sum(), -df["repayment"].sum())
    assert math.isclose(df["drawdown"].sum(),
                        inp.debt_pct_of_costs * (inp.land_cost_cr + inp.approval_cost_cr + inp.construction_cost_cr))
    # equity cf = project cf + debt flows
    recon = df["project_cf"] + df["drawdown"] + df["interest"] + df["repayment"]
    assert np.allclose(recon, df["equity_cf"])


def test_base_case_appraisal_sane():
    a = appraise(BASE_CASE)
    assert a.npv_equity_cr > 0
    assert a.irr_equity_annual is not None and 0.15 < a.irr_equity_annual < 1.0
    assert a.payback_equity_months is not None
    # NPV at the break-even price is ~0
    be = BASE_CASE.with_changes(selling_price_per_sqft=a.breakeven_price_npv_zero)
    assert abs(appraise(be).npv_equity_cr) < 1e-4
    # IRR equals the discount rate at break-even price
    assert math.isclose(appraise(be).irr_equity_annual, BASE_CASE.discount_rate, abs_tol=1e-5)


def test_no_debt_case():
    inp = BASE_CASE.with_changes(debt_pct_of_costs=0.0)
    df = build_cashflow(inp)
    assert df["drawdown"].sum() == 0 and df["interest"].sum() == 0
    a = appraise(inp, df)
    assert math.isclose(a.irr_equity_annual, a.irr_project_annual, rel_tol=1e-9)


def test_horizon_auto_extends():
    inp = BASE_CASE.with_changes(sales_end=40)
    df = build_cashflow(inp)
    assert len(df) == 46
    assert math.isclose(df["collections"].sum(), inp.gross_revenue_cr)
