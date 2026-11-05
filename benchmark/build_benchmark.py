"""Generate benchmark/base_case_benchmark.xlsx: the base case built with plain Excel formulas.

The workbook contains NO values copied from the Python model. Every cell in
CashFlow and Summary is a formula referring to the Inputs sheet, so a person
can audit it line by line, and Excel/LibreOffice computes the result
independently of the Python engine.

Usage:  python benchmark/build_benchmark.py
"""
from __future__ import annotations

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from feasibility.inputs import BASE_CASE

OUT = pathlib.Path(__file__).with_name("base_case_benchmark.xlsx")
N = BASE_CASE.effective_horizon  # 36 for the base case
FIRST, LAST = 2, N + 1            # CashFlow data rows

INPUT_ROWS = [  # (label, attribute, number_format, note)
    ("Horizon (months)", "horizon_months", "0", "Rows in CashFlow sheet"),
    ("Land cost (₹ cr)", "land_cost_cr", "0.00", ""),
    ("Land payment month", "land_month", "0", ""),
    ("Approval cost (₹ cr)", "approval_cost_cr", "0.00", ""),
    ("Approvals start month", "approval_start", "0", ""),
    ("Approvals end month", "approval_end", "0", "spread evenly"),
    ("Saleable area (sq ft)", "saleable_area_sqft", "#,##0", ""),
    ("Construction cost (₹/sq ft)", "construction_cost_per_sqft", "#,##0", ""),
    ("Construction start month", "construction_start", "0", ""),
    ("Construction end month", "construction_end", "0", "smoothstep S-curve 3x²−2x³"),
    ("Selling price (₹/sq ft)", "selling_price_per_sqft", "#,##0", ""),
    ("Sales launch month", "sales_start", "0", ""),
    ("Sales end month", "sales_end", "0", "sold evenly"),
    ("Booking collection %", "booking_pct", "0%", "collected in month of sale"),
    ("Instalment months", "instalment_months", "0", "balance spread evenly after sale"),
    ("Marketing % of collections", "marketing_pct", "0.0%", ""),
    ("Debt % of land+approval+construction", "debt_pct_of_costs", "0%", ""),
    ("Interest rate (nominal p.a.)", "interest_rate", "0.0%", "monthly = rate/12 on opening balance"),
    ("Repayment sweep % of collections", "repayment_sweep_pct", "0%", "bullet for residual in final month"),
    ("Tax rate on project profit", "tax_rate", "0%", "paid in final month"),
    ("Discount rate (effective p.a.)", "discount_rate", "0.0%", ""),
]
DERIVED_ROWS = [
    ("Construction cost total (₹ cr)", "=B9*B10/10000000", "0.00"),
    ("Gross revenue (₹ cr)", "=B9*B13/10000000", "0.00"),
    ("Monthly discount rate", "=(1+B23)^(1/12)-1", "0.000000"),
]

bold = Font(bold=True)
head_fill = PatternFill("solid", fgColor="DDEBF7")
input_fill = PatternFill("solid", fgColor="FFF2CC")


def ref(attr: str) -> str:
    """Absolute reference to an input cell on the Inputs sheet."""
    for i, (_, a, _, _) in enumerate(INPUT_ROWS):
        if a == attr:
            return f"Inputs!$B${3 + i}"
    raise KeyError(attr)


def build() -> None:
    wb = Workbook()

    # ---------------- Inputs ----------------
    ws = wb.active
    ws.title = "Inputs"
    ws["A1"] = "Base case inputs (yellow cells). Change them and the whole workbook recalculates."
    ws["A1"].font = bold
    ws.append(["Item", "Value", "Note"])
    for c in ws[2]:
        c.font = bold; c.fill = head_fill
    for label, attr, nf, note in INPUT_ROWS:
        ws.append([label, getattr(BASE_CASE, attr), note])
        ws.cell(ws.max_row, 2).number_format = nf
        ws.cell(ws.max_row, 2).fill = input_fill
    ws.append([])
    for label, formula, nf in DERIVED_ROWS:
        ws.append([label, formula, "derived"])
        ws.cell(ws.max_row, 2).number_format = nf
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 40
    # derived cell addresses
    CONSTR_TOTAL = "Inputs!$B$25"
    REVENUE = "Inputs!$B$26"
    RM = "Inputs!$B$27"

    # ---------------- CashFlow ----------------
    cf = wb.create_sheet("CashFlow")
    headers = ["Month", "Land", "Approvals", "Constr. cum. share", "Construction", "Sales booked", "Collections",
               "Marketing", "Debt opening", "Drawdown", "Interest", "Repayment", "Debt closing", "Tax",
               "Project CF", "Equity CF", "Cum. equity CF", "Cum. project CF", "Payback flag", "Disc. factor", "PV equity CF"]
    cf.append(headers)
    for c in cf[1]:
        c.font = bold; c.fill = head_fill; c.alignment = Alignment(wrap_text=True, vertical="top")
    cf.row_dimensions[1].height = 32

    # column letters
    A, B, C, D, E, F, G, H, I, J, K, L, M, Nn, O, P, Q, R, S, T, U = [get_column_letter(i) for i in range(1, 22)]
    rng = lambda col: f"${col}${FIRST}:${col}${LAST}"

    land_m, land_c = ref("land_month"), ref("land_cost_cr")
    ap_s, ap_e, ap_c = ref("approval_start"), ref("approval_end"), ref("approval_cost_cr")
    c_s, c_e = ref("construction_start"), ref("construction_end")
    s_s, s_e = ref("sales_start"), ref("sales_end")
    bk, k, mk = ref("booking_pct"), ref("instalment_months"), ref("marketing_pct")
    dp, ir, sw, tx = ref("debt_pct_of_costs"), ref("interest_rate"), ref("repayment_sweep_pct"), ref("tax_rate")
    hz = ref("horizon_months")

    for r in range(FIRST, LAST + 1):
        t = r - FIRST + 1
        prev = r - 1
        row = {
            A: t,
            B: f"=IF({A}{r}={land_m},{land_c},0)",
            C: f"=IF(AND({A}{r}>={ap_s},{A}{r}<={ap_e}),{ap_c}/({ap_e}-{ap_s}+1),0)",
            D: (f"=IF({A}{r}<{c_s},0,IF({A}{r}>{c_e},1,"
                f"3*(({A}{r}-{c_s}+1)/({c_e}-{c_s}+1))^2-2*(({A}{r}-{c_s}+1)/({c_e}-{c_s}+1))^3))"),
            E: f"=({D}{r}-{'0' if r == FIRST else D + str(prev)})*{CONSTR_TOTAL}",
            F: f"=IF(AND({A}{r}>={s_s},{A}{r}<={s_e}),{REVENUE}/({s_e}-{s_s}+1),0)",
            G: (f"={bk}*{F}{r}+IF({k}=0,(1-{bk})*{F}{r},(1-{bk})/{k}*"
                f"SUMPRODUCT(({rng(A)}>={A}{r}-{k})*({rng(A)}<={A}{r}-1)*{rng(F)}))"),
            H: f"={G}{r}*{mk}",
            I: "=0" if r == FIRST else f"={M}{prev}",
            J: f"=({B}{r}+{C}{r}+{E}{r})*{dp}",
            K: f"={I}{r}*{ir}/12",
            L: f"=IF({A}{r}={hz},{I}{r}+{J}{r},MIN({I}{r}+{J}{r},{G}{r}*{sw}))",
            M: f"={I}{r}+{J}{r}-{L}{r}",
            Nn: (f"=IF({A}{r}={hz},MAX(0,(SUM({rng(F)})-SUM({rng(B)})-SUM({rng(C)})-SUM({rng(E)})"
                 f"-SUM({rng(H)})-SUM({rng(K)}))*{tx}),0)"),
            O: f"={G}{r}-{B}{r}-{C}{r}-{E}{r}-{H}{r}-{Nn}{r}",
            P: f"={O}{r}+{J}{r}-{K}{r}-{L}{r}",
            Q: f"={P}{r}" if r == FIRST else f"={Q}{prev}+{P}{r}",
            R: f"={O}{r}" if r == FIRST else f"={R}{prev}+{O}{r}",
            S: f'=IF(AND({Q}{r}>=0,{"-1" if r == FIRST else Q + str(prev)}<0),{A}{r},"")',
            T: f"=1/(1+{RM})^{A}{r}",
            U: f"={P}{r}*{T}{r}",
        }
        for col, val in row.items():
            cell = cf[f"{col}{r}"]
            cell.value = val
            cell.number_format = "0" if col in (A, S) else ("0.0000" if col in (D, T) else "#,##0.000")
    # totals row
    tr = LAST + 1
    cf[f"{A}{tr}"] = "Total"; cf[f"{A}{tr}"].font = bold
    for col in (B, C, E, F, G, H, J, K, L, Nn, O, P, U):
        cf[f"{col}{tr}"] = f"=SUM({rng(col)})"
        cf[f"{col}{tr}"].number_format = "#,##0.000"; cf[f"{col}{tr}"].font = bold
    for i in range(1, 22):
        cf.column_dimensions[get_column_letter(i)].width = 12
    cf.freeze_panes = "B2"

    # ---------------- Summary ----------------
    sm = wb.create_sheet("Summary")
    sm.append(["Metric", "Excel value", "Formula logic"])
    for c in sm[1]:
        c.font = bold; c.fill = head_fill
    tdc = f"(SUM(CashFlow!{rng(B)})+SUM(CashFlow!{rng(C)})+SUM(CashFlow!{rng(E)})+SUM(CashFlow!{rng(H)})+SUM(CashFlow!{rng(K)}))"
    rows = [
        ("Equity NPV (₹ cr)", f"=NPV({RM},CashFlow!{rng(P)})", "0.000", "NPV(monthly rate, equity CF); first flow discounted one month"),
        ("Equity NPV check via PV column (₹ cr)", f"=SUM(CashFlow!{rng(U)})", "0.000", "sum of PV column, should equal the row above"),
        ("Equity IRR (monthly)", f"=IRR(CashFlow!{rng(P)},0.01)", "0.00000", "IRR of equity CF, guess 1%/month; not unique if the CF changes sign more than once"),
        ("Equity IRR (annual)", "=(1+B4)^12-1", "0.00%", "(1+monthly)^12 − 1"),
        ("Project NPV (₹ cr)", f"=NPV({RM},CashFlow!{rng(O)})", "0.000", "unlevered"),
        ("Project IRR (monthly)", f"=IRR(CashFlow!{rng(O)},0.01)", "0.00000", "guess 1%/month"),
        ("Project IRR (annual)", "=(1+B7)^12-1", "0.00%", ""),
        ("Payback month (equity)", f"=MIN(CashFlow!{rng(S)})", "0", "first month cumulative equity CF turns ≥ 0"),
        ("Gross revenue (₹ cr)", f"=SUM(CashFlow!{rng(F)})", "0.000", ""),
        ("Total development cost incl. interest (₹ cr)", f"={tdc}", "0.000", "land+approvals+construction+marketing+interest"),
        ("Interest (₹ cr)", f"=SUM(CashFlow!{rng(K)})", "0.000", ""),
        ("Tax (₹ cr)", f"=SUM(CashFlow!{rng(Nn)})", "0.000", ""),
        ("Pre-tax profit (₹ cr)", "=B10-B11", "0.000", ""),
        ("Post-tax profit (₹ cr)", "=B14-B13", "0.000", ""),
        ("Profit on cost, pre-tax", "=B14/B11", "0.00%", ""),
        ("Profit on cost, post-tax", "=B15/B11", "0.00%", ""),
        ("Peak debt (₹ cr)", f"=MAX(CashFlow!{rng(M)})", "0.000", ""),
        ("Peak equity requirement (₹ cr)", f"=-MIN(CashFlow!{rng(Q)})", "0.000", "most negative cumulative equity CF"),
        ("Peak equity month", f"=MATCH(MIN(CashFlow!{rng(Q)}),CashFlow!{rng(Q)},0)", "0", ""),
        ("Break-even price, NPV = 0 (₹/sq ft)", None, "#,##0", "MANUAL: Goal Seek B2 to 0 by changing Inputs!B13, record result here"),
        ("Break-even price, profit = 0 (₹/sq ft)", None, "#,##0", "MANUAL: Goal Seek B14 to 0 by changing Inputs!B13, record result here"),
    ]
    for label, formula, nf, note in rows:
        sm.append([label, formula, note])
        sm.cell(sm.max_row, 2).number_format = nf
        if formula is None:
            sm.cell(sm.max_row, 2).fill = input_fill
    sm.column_dimensions["A"].width = 44
    sm.column_dimensions["B"].width = 16
    sm.column_dimensions["C"].width = 70

    wb.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()
