"""Investment memo generation.

Two paths:
  * template_memo()  - deterministic, offline, every number comes from the model.
  * llm_memo()       - asks Claude to write the memo from a fact sheet of the
                       computed numbers. The model is instructed to use only the
                       numbers supplied and the output is checked for any figure
                       that is not in the fact sheet.
"""
from __future__ import annotations

import os
import re

from .inputs import ProjectInputs
from .metrics import Appraisal
import pandas as pd


def _pct(x: float | None, nd: int = 1) -> str:
    return "n/a" if x is None else f"{x * 100:.{nd}f}%"


def _cr(x: float | None, nd: int = 2) -> str:
    return "n/a" if x is None else f"₹{x:,.{nd}f} cr"


def _months(m: int | None) -> str:
    return "not within horizon" if m is None else f"{m} months ({m / 12:.1f} years)"


def fact_sheet(inp: ProjectInputs, a: Appraisal, scenarios: pd.DataFrame | None = None,
               tornado: pd.DataFrame | None = None) -> str:
    verdict = "VIABLE" if a.npv_equity_cr > 0 else "NOT VIABLE"
    lines = [
        "PROJECT INPUTS",
        f"- Saleable area: {inp.saleable_area_sqft:,.0f} sq ft",
        f"- Selling price: ₹{inp.selling_price_per_sqft:,.0f} per sq ft; gross revenue {_cr(a.gross_revenue_cr)}",
        f"- Land cost: {_cr(inp.land_cost_cr)} paid in month {inp.land_month}",
        f"- Construction cost: ₹{inp.construction_cost_per_sqft:,.0f} per sq ft = {_cr(a.construction_cr)}, months {inp.construction_start} to {inp.construction_end}",
        f"- Approval costs: {_cr(inp.approval_cost_cr)}",
        f"- Sales: launch month {inp.sales_start}, sold out by month {inp.sales_end}; {inp.booking_pct:.0%} on booking, balance over {inp.instalment_months} months",
        f"- Debt: {inp.debt_pct_of_costs:.0%} of land, approval and construction spend at {_pct(inp.interest_rate, 0)} p.a.; {inp.repayment_sweep_pct:.0%} of collections swept to repayment",
        f"- Income tax {_pct(inp.tax_rate, 0)}; discount rate {_pct(inp.discount_rate, 0)} p.a.",
        f"- Project horizon: {a.effective_horizon} months",
        "",
        "RESULTS",
        f"- Verdict at {_pct(inp.discount_rate, 0)} hurdle: {verdict}",
        f"- Equity NPV: {_cr(a.npv_equity_cr)}",
        f"- Equity IRR: {_pct(a.irr_equity_annual)}; Project (unlevered) IRR: {_pct(a.irr_project_annual)}"
        + ("  [WARNING: IRR is not unique for this cash flow; use NPV]" if a.irr_unreliable else ""),
        f"- Payback (equity): {_months(a.payback_equity_months)}; discounted payback: {_months(a.discounted_payback_equity_months)}",
        f"- Total development cost: {_cr(a.total_development_cost_cr)} (incl. interest {_cr(a.interest_cr)})",
        f"- Pre-tax profit: {_cr(a.pre_tax_profit_cr)}; profit on cost {_pct(a.profit_on_cost_pre_tax)} pre-tax, {_pct(a.profit_on_cost_post_tax)} post-tax",
        (f"- Break-even selling price (NPV = 0): ₹{a.breakeven_price_npv_zero:,.0f} per sq ft; "
         f"price cushion {_pct((inp.selling_price_per_sqft - a.breakeven_price_npv_zero) / inp.selling_price_per_sqft)} below the assumed price")
        if a.breakeven_price_npv_zero else "- Break-even price: not found",
        f"- Cost-covering selling price (profit = 0): ₹{a.breakeven_price_profit_zero:,.0f} per sq ft" if a.breakeven_price_profit_zero else "",
        f"- Peak equity requirement: {_cr(a.peak_equity_requirement_cr)} in month {a.peak_equity_month}",
        f"- Peak debt: {_cr(a.peak_debt_cr)}; debt fully repaid in month {a.debt_fully_repaid_month}",
    ]
    if tornado is not None and len(tornado):
        lines += ["", "SENSITIVITY (equity NPV, ₹ cr) - most influential first"]
        for _, r in tornado.sort_values("swing", ascending=False).iterrows():
            lines.append(f"- {r['driver']}: {r['low_label']} -> {r['low']:.2f}; {r['high_label']} -> {r['high']:.2f}")
    if scenarios is not None:
        lines += ["", "SCENARIOS"]
        lines += ["Scenario definitions (changes from the base case): "
                  "Downside = price -10%, construction cost +10%, sales launch delayed 6 months; "
                  "Severe downside = price -20%, construction cost +15%, sales launch delayed 12 months, interest rate +2 pp; "
                  "Upside = price +10%, construction cost -5%, sales launch 3 months earlier."]
        for name, r in scenarios.iterrows():
            lines.append(
                f"- {name}: NPV {r['NPV (₹ cr)']:.2f} cr, equity IRR {_pct(r['Equity IRR'])}, "
                f"payback {r['Payback (months)']} months, peak equity {r['Peak equity (₹ cr)']:.2f} cr"
            )
    return "\n".join(l for l in lines if l is not None)


def template_memo(inp: ProjectInputs, a: Appraisal, scenarios: pd.DataFrame | None = None,
                  tornado: pd.DataFrame | None = None, project_name: str = "the project") -> str:
    viable = a.npv_equity_cr > 0
    hurdle = _pct(inp.discount_rate, 0)
    rec = ("PROCEED, subject to the risks noted below" if viable else "DO NOT PROCEED on current assumptions")
    irr_txt = _pct(a.irr_equity_annual)
    be = a.breakeven_price_npv_zero
    cushion = (inp.selling_price_per_sqft - be) / inp.selling_price_per_sqft if be else None

    top_driver = None
    if tornado is not None and len(tornado):
        top_driver = tornado.sort_values("swing", ascending=False).iloc[0]

    parts = [
        f"INVESTMENT MEMO: {project_name}",
        "",
        "1. Recommendation",
        f"{rec}. At a {hurdle} hurdle rate the project returns an equity NPV of {_cr(a.npv_equity_cr)} "
        f"and an equity IRR of {irr_txt}, with equity paid back in {_months(a.payback_equity_months)}.",
        "",
        "2. The project",
        f"{inp.saleable_area_sqft:,.0f} sq ft of saleable area, sold at ₹{inp.selling_price_per_sqft:,.0f} per sq ft "
        f"for gross revenue of {_cr(a.gross_revenue_cr)}. Total development cost is {_cr(a.total_development_cost_cr)}: "
        f"land {_cr(a.land_cr)}, construction {_cr(a.construction_cr)}, approvals {_cr(a.approvals_cr)}, "
        f"marketing {_cr(a.marketing_cr)} and interest {_cr(a.interest_cr)}. "
        f"Pre-tax profit is {_cr(a.pre_tax_profit_cr)}, a margin of {_pct(a.profit_on_cost_pre_tax)} on cost "
        f"({_pct(a.profit_on_cost_post_tax)} after {_pct(inp.tax_rate, 0)} tax).",
        "",
        "3. Funding",
        f"The loan funds {inp.debt_pct_of_costs:.0%} of land, approval and construction spend at {_pct(inp.interest_rate, 0)}, "
        f"peaking at {_cr(a.peak_debt_cr)} and fully repaid by month {a.debt_fully_repaid_month}. "
        f"The promoters must fund a peak equity requirement of {_cr(a.peak_equity_requirement_cr)} by month {a.peak_equity_month}.",
        "",
        "4. How much cushion is there",
        (f"The selling price can fall to ₹{be:,.0f} per sq ft ({_pct(cushion)} below the assumed price) before the project "
         f"stops earning the {hurdle} hurdle. Below ₹{a.breakeven_price_profit_zero:,.0f} per sq ft it makes an outright loss."
         if be and a.breakeven_price_profit_zero else "A break-even price could not be determined."),
    ]
    if top_driver is not None:
        parts += [
            "",
            "5. Key risk drivers",
            f"The result is most sensitive to {top_driver['driver'].lower()}: moving it {top_driver['low_label']} / "
            f"{top_driver['high_label']} swings equity NPV between {_cr(top_driver['low'])} and {_cr(top_driver['high'])}.",
        ]
        others = tornado.sort_values("swing", ascending=False).iloc[1:3]
        if len(others):
            parts.append("Next in importance: " + "; ".join(
                f"{r['driver'].lower()} ({_cr(r['low'])} to {_cr(r['high'])})" for _, r in others.iterrows()) + ".")
    if scenarios is not None and "Downside" in scenarios.index:
        d = scenarios.loc["Downside"]
        parts += [
            "",
            "6. Stress test",
            f"In the downside scenario (price -10%, cost +10%, sales delayed 6 months) NPV becomes {_cr(d['NPV (₹ cr)'])} "
            f"and equity IRR {_pct(d['Equity IRR'])}, with peak equity rising to {_cr(d['Peak equity (₹ cr)'])}. "
            + ("The project still clears the hurdle under stress." if d['NPV (₹ cr)'] > 0
               else "The project does NOT clear the hurdle under stress; the decision rests on confidence in the base-case price and timeline."),
        ]
    parts += [
        "",
        "7. Limitations",
        "Deterministic monthly model; no inflation or price escalation; tax computed on total project profit and paid at the end; "
        "collections follow a fixed booking-plus-instalment pattern. All figures should be read as indicative.",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# LLM path
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You write short investment memos for real estate developers and their lenders.
You will receive a fact sheet produced by a validated financial model.
Rules:
- Use ONLY the numbers in the fact sheet. Never compute, estimate or round to a different figure.
- If a number you want is not in the fact sheet, say it is not available rather than inventing it.
- Plain language for a non-technical director. No jargon without a one-phrase explanation.
- Structure: Recommendation; The project; Funding; Cushion and break-even; Key risk drivers; Stress test; Limitations.
- Around 350-450 words. No tables. No markdown headers deeper than a plain numbered line."""


AIML_BASE_URL = "https://api.aimlapi.com/v1"
AIML_DEFAULT_MODEL = "anthropic/claude-sonnet-5-5"
ANTHROPIC_DEFAULT_MODEL = "claude-opus-5-5"
PROVIDERS = ("anthropic", "aiml")


def _env_key(provider: str) -> str | None:
    name = "ANTHROPIC_API_KEY" if provider == "anthropic" else "AIML_API_KEY"
    return os.environ.get(name) or None


def llm_available(provider: str | None = None) -> bool:
    """True if a key for the given provider (or any provider) is set in the environment."""
    if provider:
        return bool(_env_key(provider))
    return any(_env_key(p) for p in PROVIDERS)


def _user_message(fact_sheet_text: str) -> str:
    return "Fact sheet:\n\n" + fact_sheet_text + "\n\nWrite the memo."


def _anthropic_memo(fact_sheet_text: str, api_key: str | None, model: str) -> tuple[str, str]:
    """Call the Anthropic Messages API directly. Returns (text, stop_reason)."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    with client.messages.stream(
        model=model,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _user_message(fact_sheet_text)}],
    ) as stream:
        msg = stream.get_final_message()
    text = "".join(b.text for b in msg.content if b.type == "text")
    return text, msg.stop_reason or ""


def _aiml_memo(fact_sheet_text: str, api_key: str | None, model: str) -> tuple[str, str]:
    """Call the AIML API (OpenAI-compatible chat completions). Returns (text, finish_reason)."""
    import requests

    key = api_key or _env_key("aiml")
    if not key:
        raise RuntimeError("No AIML API key given and AIML_API_KEY is not set.")
    resp = requests.post(
        f"{AIML_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "max_tokens": 4000,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _user_message(fact_sheet_text)},
            ],
        },
        timeout=120,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"AIML API returned HTTP {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    choice = data["choices"][0]
    content = choice["message"].get("content") or ""
    if isinstance(content, list):  # some providers return content parts
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return content, choice.get("finish_reason") or ""


def llm_memo(
    fact_sheet_text: str,
    api_key: str | None = None,
    model: str | None = None,
    provider: str = "anthropic",
) -> tuple[str, list[str]]:
    """Return (memo_text, warnings).

    provider: "anthropic" (Anthropic Messages API, anthropic SDK) or "aiml"
    (AIML API, OpenAI-compatible endpoint that proxies Claude and other models).
    Network and HTTP errors propagate to the caller so the UI can show them and
    fall back to the template memo.
    """
    if provider not in PROVIDERS:
        raise ValueError(f"provider must be one of {PROVIDERS}, got {provider!r}")
    if provider == "anthropic":
        text, stop = _anthropic_memo(fact_sheet_text, api_key, model or ANTHROPIC_DEFAULT_MODEL)
        if stop == "refusal":
            return "", ["The model declined to write the memo (refusal stop reason)."]
    else:
        text, stop = _aiml_memo(fact_sheet_text, api_key, model or AIML_DEFAULT_MODEL)
        if stop == "content_filter":
            return "", ["The provider's content filter blocked the memo."]
    if not text.strip():
        return "", ["The model returned an empty memo."]
    warnings = check_numbers(text, fact_sheet_text)
    if stop in ("max_tokens", "length"):
        warnings.append("The memo was cut off at the token limit; the final section may be incomplete.")
    return text, warnings


_NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?")


def _norm_numbers(s: str) -> set[str]:
    out = set()
    for m in _NUM.finditer(s):
        whole = m.group(1).replace(",", "")
        frac = m.group(2) or ""
        val = float(f"{whole}.{frac}" if frac else whole)
        out.add(f"{val:.2f}")
        out.add(f"{round(val):.0f}")
        out.add(f"{val:.1f}")
    return out


def check_numbers(memo_text: str, fact_sheet_text: str) -> list[str]:
    """Flag any number in the memo that does not appear in the fact sheet (hallucination guard)."""
    allowed = _norm_numbers(fact_sheet_text)
    # section numbers 1-7 and common small integers are allowed
    allowed |= {f"{i}.00" for i in range(0, 13)} | {f"{i}" for i in range(0, 13)} | {f"{i}.0" for i in range(0, 13)}
    warnings = []
    for m in _NUM.finditer(memo_text):
        whole = m.group(1).replace(",", "")
        frac = m.group(2) or ""
        val = float(f"{whole}.{frac}" if frac else whole)
        keys = {f"{val:.2f}", f"{round(val):.0f}", f"{val:.1f}"}
        if not (keys & allowed):
            warnings.append(f"Number '{m.group(0)}' in memo is not in the model fact sheet - verify before use.")
    return sorted(set(warnings))
