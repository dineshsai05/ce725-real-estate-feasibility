"""Edge cases and validation behaviour."""
import math
import numpy as np
import pytest

from feasibility import BASE_CASE, ProjectInputs, build_cashflow, appraise
from feasibility.sensitivity import sensitivity_table, tornado, scenario_table, DRIVERS
from feasibility.memo import template_memo, fact_sheet, check_numbers


def test_invalid_inputs_are_rejected():
    bad = [
        dict(approval_end=0, approval_start=1),
        dict(construction_end=3, construction_start=4),
        dict(sales_end=6, sales_start=7),
        dict(booking_pct=1.5),
        dict(debt_pct_of_costs=-0.1),
        dict(repayment_sweep_pct=2.0),
        dict(land_month=0),
        dict(instalment_months=-1),
    ]
    for kw in bad:
        inp = BASE_CASE.with_changes(**kw)
        assert inp.validate(), kw
        with pytest.raises(ValueError):
            build_cashflow(inp)


def test_full_debt_and_zero_sweep_bullet_repayment():
    inp = BASE_CASE.with_changes(debt_pct_of_costs=1.0, repayment_sweep_pct=0.0)
    df = build_cashflow(inp)
    # no repayment until the last month, then a bullet of the whole balance
    assert (df["repayment"].iloc[:-1] == 0).all()
    assert math.isclose(-df["repayment"].iloc[-1], df["drawdown"].sum())
    assert math.isclose(df["debt_closing"].iloc[-2], df["drawdown"].sum())


def test_all_cash_at_booking():
    inp = BASE_CASE.with_changes(booking_pct=1.0, instalment_months=0)
    df = build_cashflow(inp)
    assert np.allclose(df["collections"], df["sales_booked"])


def test_zero_booking_all_instalments():
    inp = BASE_CASE.with_changes(booking_pct=0.0, instalment_months=12)
    df = build_cashflow(inp)
    assert df["collections"].iloc[inp.sales_start - 1] == 0
    assert math.isclose(df["collections"].sum(), inp.gross_revenue_cr)
    assert len(df) == inp.sales_end + 12


def test_single_month_construction_and_approvals():
    inp = BASE_CASE.with_changes(construction_start=10, construction_end=10, approval_start=2, approval_end=2)
    df = build_cashflow(inp)
    assert math.isclose(-df["construction"].iloc[9], inp.construction_cost_cr)
    assert math.isclose(-df["approvals"].iloc[1], inp.approval_cost_cr)


def test_loss_making_project_has_zero_tax_and_negative_npv():
    inp = BASE_CASE.with_changes(selling_price_per_sqft=4000)
    a = appraise(inp)
    assert a.tax_cr == 0
    assert a.pre_tax_profit_cr < 0
    assert a.npv_equity_cr < 0
    assert a.payback_equity_months is None


def test_zero_interest_rate():
    inp = BASE_CASE.with_changes(interest_rate=0.0)
    a = appraise(inp)
    assert a.interest_cr == 0
    assert a.npv_equity_cr > appraise(BASE_CASE).npv_equity_cr


def test_land_paid_late():
    inp = BASE_CASE.with_changes(land_month=12)
    df = build_cashflow(inp)
    assert -df["land"].iloc[11] == inp.land_cost_cr and df["land"].iloc[0] == 0
    # paying later is better for equity at a positive discount rate
    assert appraise(inp).npv_equity_cr > appraise(BASE_CASE).npv_equity_cr


def test_sales_before_construction_and_after_horizon():
    inp = BASE_CASE.with_changes(sales_start=2, sales_end=50, horizon_months=12)
    df = build_cashflow(inp)
    assert len(df) == 56
    assert math.isclose(df["collections"].sum(), inp.gross_revenue_cr)


def test_sensitivity_outputs_have_expected_shape():
    s = sensitivity_table(BASE_CASE)
    assert s.shape == (len(DRIVERS), 6)
    assert not s.isna().any().any()
    # the Base column equals the base NPV for every driver
    base = appraise(BASE_CASE).npv_equity_cr
    assert np.allclose(s["Base"].astype(float), base)
    # price up / cost up move in opposite directions
    assert s.loc["Selling price", "+1 step"] > base > s.loc["Construction cost", "+1 step"]
    t = tornado(BASE_CASE)
    assert list(t.sort_values("swing", ascending=False)["driver"])[0] == "Selling price"
    sc = scenario_table(BASE_CASE)
    assert sc.loc["Downside", "NPV (₹ cr)"] < sc.loc["Base case", "NPV (₹ cr)"] < sc.loc["Upside", "NPV (₹ cr)"]
    assert sc.loc["Severe downside", "NPV (₹ cr)"] < sc.loc["Downside", "NPV (₹ cr)"]


def test_template_memo_uses_only_model_numbers():
    a = appraise(BASE_CASE)
    sc = scenario_table(BASE_CASE)
    t = tornado(BASE_CASE)
    facts = fact_sheet(BASE_CASE, a, sc, t)
    memo = template_memo(BASE_CASE, a, sc, t, "Test project")
    assert check_numbers(memo, facts) == []
    assert "PROCEED" in memo


def test_number_check_flags_invented_numbers():
    facts = "Equity NPV: ₹7.45 cr\nIRR 47.2%"
    memo = "NPV is ₹7.45 cr and IRR is 47.2%. The land is worth ₹99.9 cr."
    warns = check_numbers(memo, facts)
    assert len(warns) == 1 and "99.9" in warns[0]
