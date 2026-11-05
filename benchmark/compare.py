"""Compare the Python model with the Excel benchmark after a spreadsheet recalculation.

Usage:
    python benchmark/compare.py [path/to/recalculated.xlsx]

If no path is given, the script tries to recalculate benchmark/base_case_benchmark.xlsx
with LibreOffice (headless) into benchmark/recalculated/. Prints a discrepancy table
suitable for the validation report.
"""
from __future__ import annotations

import pathlib, subprocess, sys, tempfile, shutil
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from openpyxl import load_workbook
import pandas as pd

from feasibility import BASE_CASE, build_cashflow, appraise

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "base_case_benchmark.xlsx"


def recalc_with_libreoffice(src: pathlib.Path) -> pathlib.Path:
    exe = shutil.which("libreoffice") or shutil.which("soffice")
    if not exe:
        raise SystemExit("LibreOffice not found. Open the workbook in Excel, save it, and pass its path.")
    # snap-packaged LibreOffice cannot write to /tmp, so recalculate inside the project folder
    out = HERE / "recalculated"
    out.mkdir(exist_ok=True)
    subprocess.run([exe, "--headless", "--convert-to", "xlsx", "--outdir", str(out), str(src)],
                   check=True, capture_output=True, timeout=180)
    return out / src.name


def main() -> None:
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else recalc_with_libreoffice(SRC)
    wb = load_workbook(path, data_only=True)
    sm = wb["Summary"]
    excel = {sm.cell(r, 1).value: sm.cell(r, 2).value for r in range(2, sm.max_row + 1)}

    df = build_cashflow(BASE_CASE)
    a = appraise(BASE_CASE, df)
    py = {
        "Equity NPV (₹ cr)": a.npv_equity_cr,
        "Equity NPV check via PV column (₹ cr)": a.npv_equity_cr,
        "Equity IRR (annual)": a.irr_equity_annual,
        "Project NPV (₹ cr)": a.npv_project_cr,
        "Project IRR (annual)": a.irr_project_annual,
        "Payback month (equity)": a.payback_equity_months,
        "Gross revenue (₹ cr)": a.gross_revenue_cr,
        "Total development cost incl. interest (₹ cr)": a.total_development_cost_cr,
        "Interest (₹ cr)": a.interest_cr,
        "Tax (₹ cr)": a.tax_cr,
        "Pre-tax profit (₹ cr)": a.pre_tax_profit_cr,
        "Post-tax profit (₹ cr)": a.post_tax_profit_cr,
        "Profit on cost, pre-tax": a.profit_on_cost_pre_tax,
        "Profit on cost, post-tax": a.profit_on_cost_post_tax,
        "Peak debt (₹ cr)": a.peak_debt_cr,
        "Peak equity requirement (₹ cr)": a.peak_equity_requirement_cr,
        "Peak equity month": a.peak_equity_month,
    }
    rows = []
    for k, v in py.items():
        e = excel.get(k)
        diff = None if (e is None or v is None) else float(e) - float(v)
        rows.append({"Metric": k, "Python": v, "Excel": e, "Excel − Python": diff,
                     "Match (|diff| < 1e-6)": (diff is not None and abs(diff) < 1e-6)})
    summary = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(summary.to_string(index=False))

    # month-by-month check of the two cash flow columns
    cf = wb["CashFlow"]
    hdr = [cf.cell(1, c).value for c in range(1, cf.max_column + 1)]
    col = {h: i + 1 for i, h in enumerate(hdr)}
    n = len(df)
    worst = {}
    for name, pycol in [("Collections", "collections"), ("Construction", "construction"), ("Interest", "interest"),
                        ("Repayment", "repayment"), ("Debt closing", "debt_closing"), ("Project CF", "project_cf"),
                        ("Equity CF", "equity_cf")]:
        ex = [cf.cell(r, col[name]).value or 0.0 for r in range(2, 2 + n)]
        pyv = df[pycol].abs().to_numpy() if pycol in ("construction", "interest", "repayment") else df[pycol].to_numpy()
        worst[name] = max(abs(float(e) - float(p)) for e, p in zip(ex, pyv))
    print("\nLargest absolute monthly difference per column (₹ cr):")
    for k, v in worst.items():
        print(f"  {k:14s} {v:.3e}")
    ok = summary["Match (|diff| < 1e-6)"].all() and all(v < 1e-6 for v in worst.values())
    print("\nRESULT:", "ALL MATCH" if ok else "DISCREPANCIES FOUND - see table")


if __name__ == "__main__":
    main()
