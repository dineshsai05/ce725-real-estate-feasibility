"""Second-level validation: change inputs in COPIES of the Excel benchmark, recalculate them
with LibreOffice, and compare with the Python model for the same inputs.

This proves the workbook formulas (not just the base-case numbers) agree with the engine.
Usage: python benchmark/compare_cases.py
"""
from __future__ import annotations

import pathlib, shutil, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from openpyxl import load_workbook
import pandas as pd

from feasibility import BASE_CASE, build_cashflow, appraise
from benchmark.build_benchmark import INPUT_ROWS

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "base_case_benchmark.xlsx"
OUT = HERE / "recalculated"
OUT.mkdir(exist_ok=True)

CASES = {
    "downside": dict(selling_price_per_sqft=6750.0, construction_cost_per_sqft=3300.0, sales_start=13, sales_end=30),
    "no_debt_fast_collection": dict(debt_pct_of_costs=0.0, booking_pct=1.0, instalment_months=0),
    "heavy_debt_low_sweep": dict(debt_pct_of_costs=0.9, repayment_sweep_pct=0.2, interest_rate=0.15, land_month=3),
}

METRICS = [
    ("Equity NPV (₹ cr)", "npv_equity_cr"), ("Equity IRR (annual)", "irr_equity_annual"),
    ("Project NPV (₹ cr)", "npv_project_cr"), ("Project IRR (annual)", "irr_project_annual"),
    ("Payback month (equity)", "payback_equity_months"), ("Interest (₹ cr)", "interest_cr"),
    ("Tax (₹ cr)", "tax_cr"), ("Pre-tax profit (₹ cr)", "pre_tax_profit_cr"),
    ("Peak debt (₹ cr)", "peak_debt_cr"), ("Peak equity requirement (₹ cr)", "peak_equity_requirement_cr"),
]


def make_case_workbook(name: str, changes: dict) -> pathlib.Path:
    path = OUT / f"case_{name}.xlsx"
    shutil.copy(SRC, path)
    wb = load_workbook(path)
    ws = wb["Inputs"]
    attrs = [a for _, a, _, _ in INPUT_ROWS]
    inp = BASE_CASE.with_changes(**changes)
    for i, attr in enumerate(attrs):
        ws.cell(3 + i, 2).value = getattr(inp, attr)
    # the workbook has a fixed 36 data rows; the horizon cell must equal that for the bullet/tax logic
    assert inp.effective_horizon == 36, f"case {name} needs a 36-month horizon (got {inp.effective_horizon})"
    wb.save(path)
    return path


def recalc(path: pathlib.Path) -> pathlib.Path:
    exe = shutil.which("libreoffice") or shutil.which("soffice")
    outdir = OUT / "calc"
    outdir.mkdir(exist_ok=True)
    subprocess.run([exe, "--headless", "--convert-to", "xlsx", "--outdir", str(outdir), str(path)],
                   check=True, capture_output=True, timeout=180)
    return outdir / path.name


def main():
    all_ok = True
    for name, changes in CASES.items():
        inp = BASE_CASE.with_changes(**changes)
        wb_path = recalc(make_case_workbook(name, changes))
        sm = load_workbook(wb_path, data_only=True)["Summary"]
        excel = {sm.cell(r, 1).value: sm.cell(r, 2).value for r in range(2, sm.max_row + 1)}
        a = appraise(inp)
        rows = []
        for label, attr in METRICS:
            pyv = getattr(a, attr)
            ex = excel.get(label)
            roots = getattr(a, attr.replace("_annual", "_roots"), 1) if "irr" in attr else 1
            if "irr" in attr and roots > 1:
                diff, ok = float("nan"), True
                label = label + f" [NOT UNIQUE: {roots} roots, informational]"
            elif pyv is None and (ex is None or isinstance(ex, str)):
                diff, ok = 0.0, True
            elif pyv is None or ex is None or isinstance(ex, str):
                diff, ok = float("nan"), False
            else:
                diff = float(ex) - float(pyv); ok = abs(diff) < 1e-6
            all_ok &= ok
            rows.append({"Metric": label, "Python": pyv, "Excel": ex, "Excel − Python": diff, "Match": ok})
        print(f"\n=== Case: {name} | changes: {changes}")
        pd.set_option("display.width", 200)
        print(pd.DataFrame(rows).to_string(index=False))
    print("\nRESULT:", "ALL CASES MATCH" if all_ok else "DISCREPANCIES FOUND")


if __name__ == "__main__":
    main()
