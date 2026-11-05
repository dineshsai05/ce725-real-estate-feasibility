# Validation: Python engine vs Excel benchmark (base case)

Raw comparison output. The full validation report, including three further cases, the decimal
recomputation and the discrepancy log, is in VALIDATION_REPORT.md.

Generated 30 October 2026 by `python benchmark/compare.py`. The workbook
`benchmark/base_case_benchmark.xlsx` was recalculated by LibreOffice Calc 
(headless) with no Python involvement; openpyxl then read the computed values.

| Metric | Python | Excel | Excel − Python |
|---|---|---|---|
| Equity NPV (₹ cr) | 7.451515 | 7.451515 | 0 |
| Equity IRR (annual) | 47.2344% | 47.2344% | −3.7e−12 |
| Project NPV (₹ cr) | 7.145610 | 7.145610 | 7.1e−15 |
| Project IRR (annual) | 34.2448% | 34.2448% | −3.4e−12 |
| Payback month (equity) | 27 | 27 | 0 |
| Gross revenue (₹ cr) | 75.000000 | 75.000000 | 0 |
| Total development cost incl. interest (₹ cr) | 56.518230 | 56.518230 | 2.1e−14 |
| Interest (₹ cr) | 2.018230 | 2.018230 | 2.7e−15 |
| Tax (₹ cr) | 4.620443 | 4.620443 | 0 |
| Pre-tax profit (₹ cr) | 18.481770 | 18.481770 | −1.8e−14 |
| Post-tax profit (₹ cr) | 13.861328 | 13.861328 | −3.9e−14 |
| Profit on cost, pre-tax | 32.7005% | 32.7005% | 4.4e−16 |
| Profit on cost, post-tax | 24.5254% | 24.5254% | 8.3e−17 |
| Peak debt (₹ cr) | 12.077608 | 12.077608 | 1.8e−15 |
| Peak equity requirement (₹ cr) | 12.856559 | 12.856559 | −2.8e−14 |
| Peak equity month | 8 | 8 | 0 |

Largest absolute monthly difference in any cash flow column: 5e−14 ₹ cr (floating-point noise).

Break-even prices are not in the workbook as formulas; they require Goal Seek. Python gives
₹6,250 per sq ft for NPV = 0 and ₹5,686 per sq ft for pre-tax profit = 0. The validation engineer
should reproduce both with Goal Seek and record the result in Summary!B21 and B22.

## Discrepancies found and resolved during development

| # | Discrepancy | Cause | Resolution |
|---|---|---|---|
| 1 | IRR returned "None" for the base case although NPV was clearly positive | AI-written bisection used bounds of −99% to +1000% per month; the final negative tax flow made NPV negative at both ends so no sign change was detected | Replaced with a grid scan from −50% to +100% per month for the sign change nearest zero, then bisection. Unit test added. |
| 2 | Loan was almost unused: peak debt ₹0.79 cr, interest ₹0.04 cr | First AI design funded only construction with debt; construction spend peaks after collections begin, so the 50% sweep repaid it immediately | Changed the loan to fund a share of land, approval and construction spend. Peak debt ₹12.1 cr, interest ₹2.0 cr. |
| 3 | LibreOffice reported a successful conversion but wrote no file | Snap-packaged LibreOffice cannot write to /tmp | Recalculation folder moved inside the project. |

## Manual benchmark

Months 1, 8 and 36, the discount factors, the NPV sum and the two Goal Seek prices were computed by hand
and confirmed by Surya Theja on 5 November 2026; see section 6 of `VALIDATION_REPORT.md`.
