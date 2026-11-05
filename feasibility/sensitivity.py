"""One-at-a-time sensitivity, tornado data and preset scenarios."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from .inputs import ProjectInputs
from .metrics import appraise, Appraisal


@dataclass(frozen=True)
class Driver:
    key: str
    label: str
    kind: str          # "pct" (multiply by 1+x) or "shift" (add integer months) or "abs" (add x to a rate)
    apply: Callable[[ProjectInputs, float], ProjectInputs]


def _pct(field: str):
    return lambda inp, x: inp.with_changes(**{field: getattr(inp, field) * (1 + x)})


def _rate_abs(field: str):
    return lambda inp, x: inp.with_changes(**{field: getattr(inp, field) + x})


def _sales_shift(inp: ProjectInputs, months: float) -> ProjectInputs:
    d = int(round(months))
    new_start = max(1, inp.sales_start + d)
    new_end = max(new_start, inp.sales_end + d)
    return inp.with_changes(sales_start=new_start, sales_end=new_end)


def _construction_shift(inp: ProjectInputs, months: float) -> ProjectInputs:
    d = int(round(months))
    return inp.with_changes(construction_end=max(inp.construction_start, inp.construction_end + d))


DRIVERS: list[Driver] = [
    Driver("selling_price_per_sqft", "Selling price", "pct", _pct("selling_price_per_sqft")),
    Driver("construction_cost_per_sqft", "Construction cost", "pct", _pct("construction_cost_per_sqft")),
    Driver("land_cost_cr", "Land cost", "pct", _pct("land_cost_cr")),
    Driver("approval_cost_cr", "Approval cost", "pct", _pct("approval_cost_cr")),
    Driver("sales_delay", "Sales launch delay (months)", "shift", _sales_shift),
    Driver("construction_delay", "Construction delay (months)", "shift", _construction_shift),
    Driver("interest_rate", "Interest rate (abs. change)", "abs", _rate_abs("interest_rate")),
    Driver("discount_rate", "Discount rate (abs. change)", "abs", _rate_abs("discount_rate")),
]

# default perturbation grid per kind
STEPS = {
    "pct": [-0.20, -0.10, 0.0, 0.10, 0.20],
    "shift": [-6, -3, 0, 3, 6],
    "abs": [-0.02, -0.01, 0.0, 0.01, 0.02],
}

TORNADO_SWING = {"pct": 0.10, "shift": 3, "abs": 0.02}


def _label_step(kind: str, x: float) -> str:
    if kind == "pct":
        return f"{x:+.0%}"
    if kind == "shift":
        return f"{int(x):+d} mo"
    return f"{x * 100:+.0f} pp"


STEP_UNIT = {"pct": "10%", "shift": "3 months", "abs": "1 pp"}
STEP_COLS = ["\u22122 steps", "\u22121 step", "Base", "+1 step", "+2 steps"]


def sensitivity_table(inp: ProjectInputs, metric: str = "npv_equity_cr") -> pd.DataFrame:
    """Rows = drivers; columns = 'Step' then five positional steps (-2, -1, base, +1, +2).

    Positional columns keep the table to six columns even though price/cost steps
    are percentages, delays are months and rates are percentage points.
    """
    rows = {}
    for d in DRIVERS:
        row = {"Step": STEP_UNIT[d.kind]}
        for col, x in zip(STEP_COLS, STEPS[d.kind]):
            try:
                a = appraise(d.apply(inp, x), compute_breakeven=False)
                row[col] = getattr(a, metric)
            except ValueError:
                row[col] = float("nan")
        rows[d.label] = row
    return pd.DataFrame(rows).T


def tornado(inp: ProjectInputs, metric: str = "npv_equity_cr") -> pd.DataFrame:
    """For each driver: metric at -swing, base, +swing, sorted by total swing."""
    base = getattr(appraise(inp, compute_breakeven=False), metric)
    recs = []
    for d in DRIVERS:
        s = TORNADO_SWING[d.kind]
        try:
            low = getattr(appraise(d.apply(inp, -s), compute_breakeven=False), metric)
            high = getattr(appraise(d.apply(inp, +s), compute_breakeven=False), metric)
        except ValueError:
            continue
        recs.append({
            "driver": d.label,
            "low_label": _label_step(d.kind, -s),
            "high_label": _label_step(d.kind, +s),
            "low": low,
            "base": base,
            "high": high,
            "swing": abs((high if high is not None else base) - (low if low is not None else base)),
        })
    out = pd.DataFrame(recs).sort_values("swing", ascending=True)
    return out


SCENARIOS: dict[str, dict] = {
    "Base case": {},
    "Downside": {"price": -0.10, "cost": +0.10, "sales_delay": 6},
    "Severe downside": {"price": -0.20, "cost": +0.15, "sales_delay": 12, "interest": +0.02},
    "Upside": {"price": +0.10, "cost": -0.05, "sales_delay": -3},
}


def apply_scenario(inp: ProjectInputs, spec: dict) -> ProjectInputs:
    out = inp
    if "price" in spec:
        out = out.with_changes(selling_price_per_sqft=out.selling_price_per_sqft * (1 + spec["price"]))
    if "cost" in spec:
        out = out.with_changes(construction_cost_per_sqft=out.construction_cost_per_sqft * (1 + spec["cost"]))
    if "land" in spec:
        out = out.with_changes(land_cost_cr=out.land_cost_cr * (1 + spec["land"]))
    if "sales_delay" in spec:
        out = _sales_shift(out, spec["sales_delay"])
    if "construction_delay" in spec:
        out = _construction_shift(out, spec["construction_delay"])
    if "interest" in spec:
        out = out.with_changes(interest_rate=out.interest_rate + spec["interest"])
    return out


def scenario_table(inp: ProjectInputs, scenarios: dict[str, dict] | None = None) -> pd.DataFrame:
    scenarios = scenarios or SCENARIOS
    recs = []
    for name, spec in scenarios.items():
        a: Appraisal = appraise(apply_scenario(inp, spec), compute_breakeven=False)
        recs.append({
            "Scenario": name,
            "NPV (₹ cr)": a.npv_equity_cr,
            "Equity IRR": a.irr_equity_annual,
            "Project IRR": a.irr_project_annual,
            "Payback (months)": a.payback_equity_months,
            "Profit on cost (pre-tax)": a.profit_on_cost_pre_tax,
            "Peak equity (₹ cr)": a.peak_equity_requirement_cr,
            "Peak debt (₹ cr)": a.peak_debt_cr,
            "Interest (₹ cr)": a.interest_cr,
        })
    return pd.DataFrame(recs).set_index("Scenario")
