"""Real Estate Project Feasibility and Financial Appraisal Tool - Streamlit app.

CE725 Construction Economics and Finance, IIT Bombay. Topic 2.
Run:  streamlit run app.py
"""
from __future__ import annotations

import io
import os
from dataclasses import fields

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from feasibility import BASE_CASE, ProjectInputs, build_cashflow, appraise
from feasibility.sensitivity import sensitivity_table, tornado, scenario_table, apply_scenario, SCENARIOS
from feasibility.memo import (fact_sheet, template_memo, llm_memo, check_numbers,
                              AIML_DEFAULT_MODEL, ANTHROPIC_DEFAULT_MODEL)


def _secret(name: str) -> str | None:
    """Read a key from .streamlit/secrets.toml (if present) or the environment."""
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.environ.get(name) or None

# ----------------------------------------------------------------------------
# Palette (validated default from the dataviz guide)
BLUE, ORANGE, AQUA, YELLOW, GREY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#9a9892", "#52514e"
LAYOUT = dict(
    template="plotly_white", font=dict(color="#0b0b0b"), margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    hovermode="x unified",
)

st.set_page_config(page_title="Real Estate Feasibility Appraisal", page_icon="🏗️", layout="wide")


# ----------------------------------------------------------------------------
def fmt_cr(x, nd=2):
    return "n/a" if x is None or pd.isna(x) else f"₹{x:,.{nd}f} cr"


def fmt_pct(x, nd=1):
    return "n/a" if x is None or pd.isna(x) else f"{x * 100:.{nd}f}%"


def fmt_months(m):
    return "No payback" if m is None or pd.isna(m) else f"{int(m)} mo"


def reset_inputs():
    for f in fields(ProjectInputs):
        st.session_state[f"inp_{f.name}"] = getattr(BASE_CASE, f.name)


def num(label, key, step=None, fmt=None, help=None, min_value=None, max_value=None):
    """number_input bound to session state key inp_<key>."""
    skey = f"inp_{key}"
    if skey not in st.session_state:
        st.session_state[skey] = getattr(BASE_CASE, key)
    return st.number_input(label, key=skey, step=step, format=fmt, help=help, min_value=min_value, max_value=max_value)


def pct_input(label, key, help=None):
    """Percent slider bound to a fraction field."""
    skey = f"inp_{key}"
    if skey not in st.session_state:
        st.session_state[skey] = getattr(BASE_CASE, key)
    val = st.number_input(label, value=float(st.session_state[skey]) * 100, step=0.5, format="%.1f",
                          help=help, key=f"pct_{key}", min_value=0.0, max_value=100.0)
    st.session_state[skey] = val / 100
    return val / 100


# ----------------------------------------------------------------------------
# Sidebar inputs
with st.sidebar:
    st.title("Inputs")
    st.caption("Money in ₹ crore, areas in sq ft, time in months from project start. "
               "Cash flows occur at the end of each month.")
    st.button("Reset to benchmark base case", on_click=reset_inputs, width="stretch")

    with st.expander("Timeline and land", expanded=True):
        horizon = num("Minimum horizon (months)", "horizon_months", step=1, min_value=6,
                      help="Automatically extended if sales or collections run later.")
        land_cost = num("Land cost (₹ cr)", "land_cost_cr", step=0.5, fmt="%.2f", min_value=0.0)
        land_month = num("Land payment month", "land_month", step=1, min_value=1)
        approval_cost = num("Approval and statutory costs (₹ cr)", "approval_cost_cr", step=0.25, fmt="%.2f", min_value=0.0)
        c1, c2 = st.columns(2)
        with c1:
            app_start = num("Approvals from", "approval_start", step=1, min_value=1)
        with c2:
            app_end = num("to month", "approval_end", step=1, min_value=1)

    with st.expander("Construction", expanded=True):
        area = num("Saleable area (sq ft)", "saleable_area_sqft", step=1000.0, fmt="%.0f", min_value=1000.0)
        ccost = num("Construction cost (₹ per sq ft)", "construction_cost_per_sqft", step=50.0, fmt="%.0f", min_value=0.0)
        c1, c2 = st.columns(2)
        with c1:
            c_start = num("Starts month", "construction_start", step=1, min_value=1)
        with c2:
            c_end = num("Ends month", "construction_end", step=1, min_value=1)
        st.caption("Spend follows a smoothstep S-curve: cumulative share = 3x² − 2x³.")

    with st.expander("Sales and collections", expanded=True):
        price = num("Selling price (₹ per sq ft)", "selling_price_per_sqft", step=100.0, fmt="%.0f", min_value=0.0)
        c1, c2 = st.columns(2)
        with c1:
            s_start = num("Launch month", "sales_start", step=1, min_value=1)
        with c2:
            s_end = num("Sold out by month", "sales_end", step=1, min_value=1)
        booking = pct_input("Collected at booking (%)", "booking_pct")
        inst = num("Balance collected over (months)", "instalment_months", step=1, min_value=0)
        mkt = pct_input("Marketing and brokerage (% of collections)", "marketing_pct")

    with st.expander("Financing", expanded=True):
        debt_pct = pct_input("Loan funds this share of land, approval and construction spend (%)", "debt_pct_of_costs")
        rate = pct_input("Interest rate (% p.a., nominal, monthly interest = balance × rate/12)", "interest_rate")
        sweep = pct_input("Share of monthly collections swept to repay loan (%)", "repayment_sweep_pct",
                          help="Any balance left in the final month is repaid as a bullet.")

    with st.expander("Tax and appraisal", expanded=True):
        tax = pct_input("Income tax on project profit (%)", "tax_rate",
                        help="Applied to total project profit (revenue − all costs − interest) and paid in the final month.")
        disc = pct_input("Discount rate (% p.a., effective)", "discount_rate",
                         help="Monthly rate = (1 + annual)^(1/12) − 1. NPV is computed on equity cash flows.")

inp = ProjectInputs(
    horizon_months=int(horizon), land_cost_cr=float(land_cost), land_month=int(land_month),
    approval_cost_cr=float(approval_cost), approval_start=int(app_start), approval_end=int(app_end),
    saleable_area_sqft=float(area), construction_cost_per_sqft=float(ccost),
    construction_start=int(c_start), construction_end=int(c_end),
    selling_price_per_sqft=float(price), sales_start=int(s_start), sales_end=int(s_end),
    booking_pct=booking, instalment_months=int(inst), marketing_pct=mkt,
    debt_pct_of_costs=debt_pct, interest_rate=rate, repayment_sweep_pct=sweep,
    tax_rate=tax, discount_rate=disc,
)

# ----------------------------------------------------------------------------
st.title("Real Estate Project Feasibility and Financial Appraisal")
st.caption("CE725 Construction Economics and Finance · Topic 2 · Every figure is reproducible in the benchmark workbook.")

problems = inp.validate()
if problems:
    for p in problems:
        st.error(p)
    st.stop()


@st.cache_data(show_spinner=False)
def run_all(inp_dict: dict):
    inp_ = ProjectInputs(**inp_dict)
    df_ = build_cashflow(inp_)
    a_ = appraise(inp_, df_)
    tor_ = tornado(inp_)
    scen_ = scenario_table(inp_)
    return df_, a_, tor_, scen_


df, a, tor, scen = run_all(inp.to_dict())

# KPI rows -------------------------------------------------------------------
viable = a.npv_equity_cr > 0
st.markdown(f"### Verdict: {'✅ Viable' if viable else '❌ Not viable'} at a {fmt_pct(inp.discount_rate, 0)} hurdle rate")
k = st.columns(5)
k[0].metric("Equity NPV", fmt_cr(a.npv_equity_cr))
k[1].metric("Equity IRR (annual)", fmt_pct(a.irr_equity_annual) + (" ⚠" if a.irr_unreliable else ""))
k[2].metric("Payback (equity)", fmt_months(a.payback_equity_months))
k[3].metric("Profit on cost (pre-tax)", fmt_pct(a.profit_on_cost_pre_tax))
k[4].metric("Break-even price (NPV = 0)", f"₹{a.breakeven_price_npv_zero:,.0f}/sq ft" if a.breakeven_price_npv_zero else "n/a",
            delta=f"{(a.breakeven_price_npv_zero / inp.selling_price_per_sqft - 1) * 100:+.1f}% vs assumed" if a.breakeven_price_npv_zero else None,
            delta_color="inverse")
k2 = st.columns(5)
k2[0].metric("Project (unlevered) IRR", fmt_pct(a.irr_project_annual))
k2[1].metric("Peak equity requirement", fmt_cr(a.peak_equity_requirement_cr), help=f"Month {a.peak_equity_month}")
k2[2].metric("Peak debt", fmt_cr(a.peak_debt_cr), help=f"Debt-free from month {a.debt_fully_repaid_month}")
k2[3].metric("Total interest", fmt_cr(a.interest_cr))
k2[4].metric("Horizon used", f"{a.effective_horizon} months")

if a.irr_unreliable:
    st.warning(f"Equity IRR is not reliable for this cash flow: it changes sign {a.equity_sign_changes} times and "
               f"{a.irr_equity_roots} rate(s) in the plausible range give NPV = 0, "
               + ("and the IRR shown disagrees with the sign of NPV at the hurdle rate. " if a.irr_equity_roots <= 1 else "so the IRR is not unique. ")
               + "Decide on NPV at the hurdle rate, not on IRR. This usually happens with a large bullet repayment at the end.")

tabs = st.tabs(["Summary", "Cash flow", "Sensitivity", "Scenarios", "Investment memo", "Assumptions and validation"])

# --- Summary ------------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.subheader("Where the money goes")
        cost_items = pd.DataFrame({
            "item": ["Land", "Construction", "Approvals", "Marketing", "Interest", "Tax"],
            "cr": [abs(v) + 0.0 for v in (a.land_cr, a.construction_cr, a.approvals_cr, a.marketing_cr, a.interest_cr, a.tax_cr)],
        }).sort_values("cr", ascending=True)
        fig = go.Figure(go.Bar(x=cost_items["cr"], y=cost_items["item"], orientation="h", marker_color=BLUE,
                               text=[f"₹{v:,.2f} cr" for v in cost_items["cr"]], textposition="outside",
                               hovertemplate="%{y}: ₹%{x:,.2f} cr<extra></extra>"))
        fig.update_layout(**{**LAYOUT, "hovermode": "closest"}, height=320, xaxis_title="₹ crore",
                          xaxis=dict(range=[0, cost_items["cr"].max() * 1.3]))
        st.plotly_chart(fig, width="stretch")
        summary = pd.DataFrame({
            "₹ crore": {
                "Gross revenue": a.gross_revenue_cr,
                "Total development cost (incl. interest)": a.total_development_cost_cr,
                "Pre-tax profit": a.pre_tax_profit_cr,
                "Tax": a.tax_cr,
                "Post-tax profit": a.post_tax_profit_cr,
                "Equity NPV @ hurdle": a.npv_equity_cr,
                "Project NPV @ hurdle": a.npv_project_cr,
            }
        })
        st.dataframe(summary.style.format("{:,.2f}"), width="stretch")
    with c2:
        st.subheader("Cumulative outflow vs collections (S-curves)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=-df["cum_outflow"], name="Cumulative development spend", line=dict(color=ORANGE, width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df["cum_collections"], name="Cumulative collections", line=dict(color=BLUE, width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df["cum_equity_cf"], name="Cumulative equity cash flow", line=dict(color=AQUA, width=2, dash="dot")))
        fig.add_hline(y=0, line_color=GREY, line_width=1)
        fig.update_layout(**LAYOUT, height=420, xaxis_title="Month", yaxis_title="₹ crore")
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Equity is deepest in the hole in month {a.peak_equity_month} at {fmt_cr(a.peak_equity_requirement_cr)}; "
                   f"cumulative equity cash turns positive in {fmt_months(a.payback_equity_months)}.")

# --- Cash flow ------------------------------------------------------------------
with tabs[1]:
    st.subheader("Monthly cash flow (₹ crore, inflows +, outflows −)")
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index, y=df["collections"], name="Collections", marker_color=BLUE))
        fig.add_trace(go.Bar(x=df.index, y=df["land"] + df["approvals"] + df["construction"] + df["marketing"], name="Development spend", marker_color=ORANGE))
        fig.add_trace(go.Bar(x=df.index, y=df["interest"] + df["tax"], name="Interest and tax", marker_color=YELLOW))
        fig.add_trace(go.Scatter(x=df.index, y=df["equity_cf"], name="Net equity cash flow", line=dict(color=INK, width=2)))
        fig.update_layout(**LAYOUT, barmode="relative", height=380, xaxis_title="Month", yaxis_title="₹ crore")
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index, y=df["drawdown"], name="Drawdown", marker_color=BLUE))
        fig.add_trace(go.Bar(x=df.index, y=df["repayment"], name="Repayment", marker_color=ORANGE))
        fig.add_trace(go.Scatter(x=df.index, y=df["debt_closing"], name="Closing loan balance", line=dict(color=INK, width=2)))
        fig.update_layout(**LAYOUT, barmode="relative", height=380, xaxis_title="Month", yaxis_title="₹ crore")
        st.plotly_chart(fig, width="stretch")

    show_cols = ["land", "approvals", "construction", "marketing", "sales_booked", "collections", "tax", "project_cf",
                 "debt_opening", "drawdown", "interest", "repayment", "debt_closing", "equity_cf", "cum_equity_cf"]
    nice = {"land": "Land", "approvals": "Approvals", "construction": "Construction", "marketing": "Marketing",
            "sales_booked": "Sales booked", "collections": "Collections", "tax": "Tax", "project_cf": "Project CF",
            "debt_opening": "Debt opening", "drawdown": "Drawdown", "interest": "Interest", "repayment": "Repayment",
            "debt_closing": "Debt closing", "equity_cf": "Equity CF", "cum_equity_cf": "Cum. equity CF"}
    table = df[show_cols].rename(columns=nice)
    totals = table.sum(numeric_only=True).to_frame().T
    totals.index = ["Total"]
    totals.loc["Total", ["Debt opening", "Debt closing", "Cum. equity CF"]] = float("nan")
    table.index = [str(i) for i in table.index]
    st.dataframe(pd.concat([table, totals]).style.format("{:,.3f}", na_rep=""), width="stretch", height=520)
    st.download_button("Download cash flow (CSV)", df.to_csv().encode(), "cashflow.csv", "text/csv")

# --- Sensitivity ------------------------------------------------------------------
with tabs[2]:
    metric_label = st.radio("Metric", ["Equity NPV (₹ cr)", "Equity IRR", "Project IRR", "Profit on cost (pre-tax)"], horizontal=True)
    metric_key = {"Equity NPV (₹ cr)": "npv_equity_cr", "Equity IRR": "irr_equity_annual",
                  "Project IRR": "irr_project_annual", "Profit on cost (pre-tax)": "profit_on_cost_pre_tax"}[metric_label]
    is_pct = metric_key != "npv_equity_cr"

    c1, c2 = st.columns([1.1, 1])
    with c1:
        st.subheader("One-at-a-time sensitivity")
        st.caption("Each row varies a single input while all others stay at the current inputs. A step is 10% for price and costs, "
                   "3 months for delays and 1 percentage point for rates. For delays, +1 step means 3 months later.")
        sens = sensitivity_table(inp, metric_key)
        fmt = (lambda v: fmt_pct(v)) if is_pct else (lambda v: f"{v:,.2f}")
        num_cols = [c for c in sens.columns if c != "Step"]
        st.dataframe(sens.style.format(fmt, subset=num_cols, na_rep="n/a"), width="stretch")
    with c2:
        st.subheader("Tornado: which input matters most")
        t = tornado(inp, metric_key) if metric_key != "npv_equity_cr" else tor
        t = t.dropna(subset=["low", "high"])
        base_v = t["base"].iloc[0] if len(t) else 0
        # colour by the DIRECTION OF THE METRIC, not of the input: orange = metric falls, blue = metric rises
        worse = t[["low", "high"]].min(axis=1)
        better = t[["low", "high"]].max(axis=1)
        worse_lbl = [r["low_label"] if r["low"] <= r["high"] else r["high_label"] for _, r in t.iterrows()]
        better_lbl = [r["high_label"] if r["low"] <= r["high"] else r["low_label"] for _, r in t.iterrows()]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=t["driver"], x=worse - base_v, base=base_v, orientation="h", name="Metric falls (adverse)",
                             marker_color=ORANGE, customdata=list(zip(worse_lbl, worse)),
                             hovertemplate="%{y} %{customdata[0]}: %{customdata[1]:,.3f}<extra></extra>"))
        fig.add_trace(go.Bar(y=t["driver"], x=better - base_v, base=base_v, orientation="h", name="Metric rises (favourable)",
                             marker_color=BLUE, customdata=list(zip(better_lbl, better)),
                             hovertemplate="%{y} %{customdata[0]}: %{customdata[1]:,.3f}<extra></extra>"))
        fig.add_vline(x=base_v, line_color=INK, line_width=1)
        fig.update_layout(**{**LAYOUT, "hovermode": "closest"}, barmode="overlay", height=420,
                          xaxis_title=metric_label, xaxis=dict(tickformat=".0%" if is_pct else ",.1f"))
        st.plotly_chart(fig, width="stretch")
        st.caption("Swing used: ±10% for price and costs, ±3 months for delays, ±2 percentage points for rates. "
                   "Orange = the metric falls, blue = the metric rises. Hover a bar to see which direction of the input caused it.")

# --- Scenarios ------------------------------------------------------------------
with tabs[3]:
    st.subheader("Preset scenarios")
    st.caption("Downside: price −10%, construction cost +10%, launch delayed 6 months. "
               "Severe: price −20%, cost +15%, launch delayed 12 months, interest +2 pp. "
               "Upside: price +10%, cost −5%, launch 3 months earlier.")
    st.dataframe(scen.style.format({
        "NPV (₹ cr)": "{:,.2f}", "Equity IRR": lambda v: fmt_pct(v), "Project IRR": lambda v: fmt_pct(v),
        "Payback (months)": lambda v: fmt_months(v), "Profit on cost (pre-tax)": lambda v: fmt_pct(v),
        "Peak equity (₹ cr)": "{:,.2f}", "Peak debt (₹ cr)": "{:,.2f}", "Interest (₹ cr)": "{:,.2f}",
    }, na_rep="n/a"), width="stretch")

    st.subheader("Custom stress test")
    c = st.columns(5)
    sp = c[0].slider("Price change", -40, 40, 0, 5, format="%d%%") / 100
    sc = c[1].slider("Construction cost change", -30, 50, 0, 5, format="%d%%") / 100
    sl = c[2].slider("Land cost change", -30, 50, 0, 5, format="%d%%") / 100
    sd = c[3].slider("Sales launch delay (months)", -6, 24, 0, 1)
    si = c[4].slider("Interest rate change (pp)", -4.0, 6.0, 0.0, 0.5) / 100
    custom = apply_scenario(inp, {"price": sp, "cost": sc, "land": sl, "sales_delay": sd, "interest": si})
    ca = appraise(custom)
    cc = st.columns(5)
    cc[0].metric("Equity NPV", fmt_cr(ca.npv_equity_cr), delta=f"{ca.npv_equity_cr - a.npv_equity_cr:+.2f} cr")
    cc[1].metric("Equity IRR", fmt_pct(ca.irr_equity_annual))
    cc[2].metric("Payback", fmt_months(ca.payback_equity_months))
    cc[3].metric("Peak equity", fmt_cr(ca.peak_equity_requirement_cr))
    cc[4].metric("Horizon", f"{ca.effective_horizon} mo")

    fig = go.Figure()
    cdf = build_cashflow(custom)
    fig.add_trace(go.Scatter(x=df.index, y=df["cum_equity_cf"], name="Base case", line=dict(color=GREY, width=2)))
    fig.add_trace(go.Scatter(x=cdf.index, y=cdf["cum_equity_cf"], name="Custom scenario", line=dict(color=BLUE, width=2)))
    fig.add_hline(y=0, line_color=INK, line_width=1)
    fig.update_layout(**LAYOUT, height=340, xaxis_title="Month", yaxis_title="Cumulative equity cash flow (₹ cr)")
    st.plotly_chart(fig, width="stretch")

# --- Memo ------------------------------------------------------------------
with tabs[4]:
    st.subheader("Plain-language investment memo")
    project_name = st.text_input("Project name", "Proposed residential development")
    facts = fact_sheet(inp, a, scen, tor)
    mode = st.radio("Generate with", ["Template (offline, deterministic)", "Claude (LLM, needs API key)"], horizontal=True)
    if mode.startswith("Template"):
        memo = template_memo(inp, a, scen, tor, project_name)
        st.text_area("Memo", memo, height=520)
        st.download_button("Download memo (.txt)", memo.encode(), "investment_memo.txt")
    else:
        provider_label = st.selectbox(
            "Provider",
            ["AIML API (OpenAI-compatible gateway, Claude models)", "Anthropic API (direct)"],
            help="Both send the same fact sheet and system prompt. AIML API is a third-party gateway; "
                 "Anthropic API calls Anthropic directly.",
        )
        provider = "aiml" if provider_label.startswith("AIML") else "anthropic"
        env_name = "AIML_API_KEY" if provider == "aiml" else "ANTHROPIC_API_KEY"
        default_model = AIML_DEFAULT_MODEL if provider == "aiml" else ANTHROPIC_DEFAULT_MODEL
        stored_key = _secret(env_name)
        key = st.text_input(
            f"API key (not stored; leave blank to use {env_name} from secrets or the environment)",
            type="password",
        )
        model = st.text_input("Model", default_model)
        if stored_key and not key:
            st.caption(f"Using the {env_name} configured for this app.")
        st.caption("The model receives only the fact sheet below and is instructed to use no other numbers. "
                   "Every number in its output is checked against the fact sheet; anything unmatched is flagged. "
                   "The team must still read and verify the memo before use. "
                   f"Fact sheet contents are sent to {'the AIML API' if provider == 'aiml' else 'Anthropic'} over the internet.")
        if st.button("Generate memo with Claude"):
            try:
                with st.spinner("Writing memo..."):
                    memo, warns = llm_memo(facts, api_key=key or stored_key or None, model=model.strip() or None,
                                           provider=provider)
                st.session_state["llm_memo"] = (memo, warns)
            except Exception as e:  # surfaced to the user; template remains available
                st.error(f"Could not generate memo: {type(e).__name__}: {e}")
        if "llm_memo" in st.session_state:
            memo, warns = st.session_state["llm_memo"]
            if warns:
                st.warning("Numbers in the memo that are not in the model fact sheet:\n\n- " + "\n- ".join(warns))
            else:
                st.success("Every number in the memo matches the model fact sheet.")
            st.text_area("Memo (LLM draft - verify before use)", memo, height=520)
            st.download_button("Download memo (.txt)", memo.encode(), "investment_memo_llm.txt")
    with st.expander("Fact sheet given to the memo writer"):
        st.code(facts)

# --- Assumptions and validation ------------------------------------------------
with tabs[5]:
    st.subheader("Model assumptions")
    st.markdown(f"""
1. **Timing.** All cash flows occur at the end of the month. Month 1 is discounted one full period, matching Excel's `NPV()`.
2. **Land** is a single payment in month {inp.land_month}. **Approvals** are spread evenly over months {inp.approval_start} to {inp.approval_end}.
3. **Construction** spend of ₹{inp.construction_cost_per_sqft:,.0f}/sq ft × {inp.saleable_area_sqft:,.0f} sq ft follows a smoothstep S-curve
   (cumulative share 3x² − 2x³) over months {inp.construction_start} to {inp.construction_end}.
4. **Sales** are booked evenly from month {inp.sales_start} to {inp.sales_end}. Of each booking, {inp.booking_pct:.0%} is collected immediately
   and the balance in {inp.instalment_months} equal monthly instalments. Marketing is {inp.marketing_pct:.1%} of collections.
5. **Debt** funds {inp.debt_pct_of_costs:.0%} of each month's land, approval and construction spend. Interest = opening balance × {inp.interest_rate:.1%}/12, paid in cash monthly.
   Repayment each month = min(balance, {inp.repayment_sweep_pct:.0%} × collections); any residual is repaid in the final month.
6. **Tax** of {inp.tax_rate:.0%} on total project profit (revenue − land − approvals − construction − marketing − interest), paid in the final month if positive.
7. **Equity cash flow** = project cash flow + drawdown − interest − repayment. NPV and IRR are reported on equity cash flows (levered);
   the unlevered project IRR is also shown. Monthly discount rate = (1 + {inp.discount_rate:.1%})^(1/12) − 1.
8. **Break-even price** is found by bisection on the selling price until equity NPV = 0 (and separately until pre-tax profit = 0).
9. **Not modelled:** inflation or price escalation, GST, stamp duty, unsold inventory, cost overruns beyond the sensitivity inputs, and lender covenants.
""")
    st.subheader("Validation against the manual benchmark")
    st.markdown("""
The file `benchmark/base_case_benchmark.xlsx` reproduces the base case with plain Excel formulas and no Python.
Open it, let Excel recalculate, and compare its Summary sheet with the figures above with the sidebar reset to the base case.
Run `python benchmark/compare.py` to produce the discrepancy table automatically after a recalculation.
""")
    bench = os.path.join(os.path.dirname(__file__), "benchmark", "base_case_benchmark.xlsx")
    if os.path.exists(bench):
        with open(bench, "rb") as f:
            st.download_button("Download benchmark workbook", f.read(), "base_case_benchmark.xlsx")
    st.download_button("Download current inputs (JSON)", pd.Series(inp.to_dict()).to_json(indent=2).encode(), "inputs.json")
