# Validation Report

Real Estate Project Feasibility and Financial Appraisal Tool. CE725 Course Project, Topic 2.
Prepared 30 October 2026. Validation Engineer: Surya Theja. Figures below were produced by the
scripts named in each section; the team member responsible must re-run them and sign off.

## 1. What was validated and how

The course requires the base case to be recomputed without AI assistance and compared with the
tool. We used four layers of checking, from most independent to least.

| Layer | Independence from the Python engine | Script or file |
|---|---|---|
| A. Excel benchmark workbook recalculated by LibreOffice Calc | Different calculation engine, plain spreadsheet formulas, no values copied from Python | `benchmark/base_case_benchmark.xlsx`, `benchmark/compare.py` |
| B. Three additional input cases run through copies of the workbook | Same formulas, different inputs: tests the formulas, not just one set of numbers | `benchmark/compare_cases.py` |
| C. Decimal-arithmetic recomputation written from the assumptions list, not from the model code | Independent re-implementation, exact decimal arithmetic | `benchmark/hand_check.py` |
| D. 383 automated tests: hand-worked examples, accounting identities on 200 random input sets, comparison with the `numpy_financial` library | Checks internal consistency and third-party agreement | `tests/` |

Layer A and C are AI-assisted artefacts. The hand calculation the course asks for is described in
section 6 and must be done by the Validation Engineer with a calculator and recorded there.

## 2. Base case

| Item | Value |
|---|---|
| Saleable area | 1,00,000 sq ft |
| Selling price | ₹7,500 per sq ft (gross revenue ₹75 crore) |
| Land | ₹20 crore, month 1 |
| Approvals | ₹3 crore, months 1 to 3 |
| Construction | ₹3,000 per sq ft (₹30 crore), months 4 to 30, smoothstep S-curve |
| Sales | months 7 to 30, 20% at booking, balance over 6 months; marketing 2% of collections |
| Debt | 50% of land, approval and construction spend at 12% p.a.; 50% of collections swept to repayment |
| Tax | 25% of project profit, paid in month 36 |
| Discount rate | 15% p.a. effective; monthly rate 1.171492% |

## 3. Layer A: Excel benchmark vs tool, base case

| Metric | Tool (Python) | Excel (LibreOffice recalculation) | Excel − Python | Match |
|---|---|---|---|---|
| Equity NPV (₹ cr) | 7.451515 | 7.451515 | 0 | Yes |
| Equity NPV via PV column (₹ cr) | 7.451515 | 7.451515 | 0 | Yes |
| Equity IRR (annual) | 47.2344% | 47.2344% | −3.7e−12 | Yes |
| Project NPV (₹ cr) | 7.145610 | 7.145610 | 7e−15 | Yes |
| Project IRR (annual) | 34.2448% | 34.2448% | −3.4e−12 | Yes |
| Payback month (equity) | 27 | 27 | 0 | Yes |
| Gross revenue (₹ cr) | 75.000000 | 75.000000 | 0 | Yes |
| Total development cost incl. interest (₹ cr) | 56.518230 | 56.518230 | 2e−14 | Yes |
| Interest (₹ cr) | 2.018230 | 2.018230 | 3e−15 | Yes |
| Tax (₹ cr) | 4.620443 | 4.620443 | 0 | Yes |
| Pre-tax profit (₹ cr) | 18.481770 | 18.481770 | −2e−14 | Yes |
| Post-tax profit (₹ cr) | 13.861328 | 13.861328 | −4e−14 | Yes |
| Profit on cost, pre-tax | 32.7005% | 32.7005% | 4e−16 | Yes |
| Profit on cost, post-tax | 24.5254% | 24.5254% | 8e−17 | Yes |
| Peak debt (₹ cr) | 12.077608 | 12.077608 | 2e−15 | Yes |
| Peak equity requirement (₹ cr) | 12.856559 | 12.856559 | −3e−14 | Yes |
| Peak equity month | 8 | 8 | 0 | Yes |

Largest difference in any monthly cash flow column: 5e−14 crore. All differences are floating-point
noise. Break-even prices are not formulas in the workbook; see section 6.

## 4. Layer B: three further cases through the workbook formulas

| Case | Changes from base | Metrics compared | Result |
|---|---|---|---|
| Downside | Price ₹6,750, cost ₹3,300/sq ft, sales months 13 to 30 | NPV, IRRs, payback, interest, tax, profit, peak debt, peak equity | All 10 match within 1e−12 |
| No debt, all cash at booking | Debt 0%, booking 100%, no instalments | Same 10 | All match; equity = project metrics exactly, as expected |
| Heavy debt, low sweep | Debt 90%, sweep 20%, interest 15%, land in month 3 | Same 10 | Cash flow metrics match; equity IRR differs (see discrepancy 4) |

## 5. Layer C: independent decimal recomputation of selected months

Computed by `benchmark/hand_check.py` from the written assumptions with Python's exact decimal type.
Values in ₹ crore. Discount factor DF = 1 ÷ 1.01171492^t.

| Month | Land | Approvals | Construction | Sales booked | Collections | Drawdown | Interest | Repayment | Debt closing | Project CF | Equity CF | DF | PV |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20.000 | 1.000 | 0 | 0 | 0 | 10.5000 | 0 | 0 | 10.5000 | −21.0000 | −10.5000 | 0.988421 | −10.3784 |
| 2 | 0 | 1.000 | 0 | 0 | 0 | 0.5000 | 0.10500 | 0 | 11.0000 | −1.0000 | −0.6050 | 0.976976 | −0.5911 |
| 8 | 0 | 0 | 0.9252 | 3.125 | 1.0417 | 0.4626 | 0.12078 | 0.5208 | 12.0194 | 0.0957 | −0.0834 | 0.911034 | −0.0759 |
| 12 | 0 | 0 | 1.4373 | 3.125 | 2.7083 | 0.7186 | 0.11024 | 1.3542 | 10.3889 | 1.2169 | 0.4711 | 0.869565 | 0.4097 |
| 20 | 0 | 0 | 1.5836 | 3.125 | 3.1250 | 0.7918 | 0.05122 | 1.5625 | 4.3513 | 1.4789 | 0.6570 | 0.792204 | 0.5205 |
| 30 | 0 | 0 | 0.1204 | 3.125 | 3.1250 | 0.0602 | 0 | 0.0602 | 0 | 2.9421 | 2.9421 | 0.705108 | 2.0745 |
| 31 | 0 | 0 | 0 | 0 | 2.5000 | 0 | 0 | 0 | 0 | 2.4500 | 2.4500 | 0.696943 | 1.7075 |
| 36 | 0 | 0 | 0 | 0 | 0.4167 | 0 | 0 | 0 | 0 | −4.2121 | −4.2121 | 0.657516 | −2.7695 |

Sum of PV over all 36 months = 7.451515 crore. Engine NPV = 7.451515 crore. Difference 4.6e−14.
Largest monthly equity cash flow difference 1.5e−14 crore.

Worked example, month 8, for a reader checking by calculator:
- Construction window is 27 months (4 to 30); month 8 is k = 5. Cumulative share S(5/27) = 3(0.18519)² − 2(0.18519)³ = 0.09018; S(4/27) = 0.05935. Spend = (0.09018 − 0.05935) × 30 = 0.9252 crore.
- Sales booked = 75 ÷ 24 = 3.125 crore per month from month 7. Collections in month 8 = 20% × 3.125 + (80% ÷ 6) × 3.125 (instalment on month 7's sale) = 0.625 + 0.4167 = 1.0417 crore.
- Drawdown = 50% × 0.9252 = 0.4626. Interest = opening 12.0776 × 12% ÷ 12 = 0.12078. Repayment = min(12.0776 + 0.4626, 50% × 1.0417) = 0.5208. Closing = 12.0776 + 0.4626 − 0.5208 = 12.0194.
- Project CF = 1.0417 − 0.9252 − 0.0208 (marketing 2%) = 0.0957. Equity CF = 0.0957 + 0.4626 − 0.1208 − 0.5208 = −0.0834.

## 6. Manual benchmark: months 1, 8, 36 and the NPV by calculator

**Status.** First pass prepared on 5 November 2026 by the AI assistant (Claude Code) using calculator-style
arithmetic: every intermediate value rounded to 4 decimals in ₹ crore and factors to 6 decimals, exactly as a
person with a hand calculator would do it, and without calling the Python engine for any intermediate
value. The only figures read off the workbook are the ones a person would also read off it (the month-7
closing debt, the total interest, and the equity cash flow column for the NPV sum). **The course requires
this to be re-performed by a team member without AI. Surya Theja (Validation Engineer) is to repeat every
line below with a calculator, tick each one, and sign the table.** Any line that does not reproduce is a
finding and goes in section 7.

### 6.1 Constants

- Monthly discount rate m = 1.15^(1/12) − 1 = **0.011715**
- Monthly sales booked = 75 ÷ 24 = **3.1250** crore (months 7 to 30)
- Construction window = months 4 to 30 = 27 months; total construction = 1,00,000 × 3,000 = **30.0000** crore
- Marketing = 2% of collections; instalment share per month = 0.80 ÷ 6 = 0.133333 of a booking

### 6.2 Month 1

| Step | Calculation | Value |
|---|---|---|
| Land | paid in month 1 | 20.0000 |
| Approvals | 3 ÷ 3 months | 1.0000 |
| Construction, sales, collections | window not started | 0 |
| Drawdown | 50% × (20 + 1 + 0) | 10.5000 |
| Interest | opening debt 0 × 1% | 0 |
| Repayment | 50% × collections 0 | 0 |
| Project CF | 0 − 20 − 1 | **−21.0000** |
| Equity CF | −21.0000 + 10.5000 − 0 − 0 | **−10.5000** |

### 6.3 Month 8

| Step | Calculation | Value |
|---|---|---|
| S-curve position | k = 8 − 4 + 1 = 5; x₅ = 5 ÷ 27 = 0.185185; x₄ = 4 ÷ 27 = 0.148148 | |
| Cumulative share S(x₅) | 3(0.185185)² − 2(0.185185)³ = 0.102881 − 0.012702 | 0.090179 |
| Cumulative share S(x₄) | 3(0.148148)² − 2(0.148148)³ = 0.065844 − 0.006504 | 0.059340 |
| Construction spend | (0.090179 − 0.059340) × 30 | 0.9252 |
| Collections | 20% × 3.1250 (month-8 booking) + 0.133333 × 3.1250 (instalment on month-7 booking) = 0.6250 + 0.4167 | 1.0417 |
| Marketing | 2% × 1.0417 | 0.0208 |
| Opening debt | closing debt of month 7, read from workbook row 7 | 12.0776 |
| Drawdown | 50% × 0.9252 | 0.4626 |
| Interest | 12.0776 × 0.12 ÷ 12 | 0.1208 |
| Repayment | min(12.0776 + 0.4626, 50% × 1.0417) = min(12.5402, 0.5209) | 0.5209 |
| Project CF | 1.0417 − 0.9252 − 0.0208 | **0.0957** |
| Equity CF | 0.0957 + 0.4626 − 0.1208 − 0.5209 | **−0.0834** |

### 6.4 Month 36

| Step | Calculation | Value |
|---|---|---|
| Collections | last instalment on the month-30 booking: 0.133333 × 3.1250 | 0.4167 |
| Marketing | 2% × 0.4167 | 0.0083 |
| Total marketing (all months) | 2% × 75 | 1.5000 |
| Total interest | sum of the interest column, read from workbook Summary!B12 | 2.0182 |
| Pre-tax profit | 75 − 20 − 3 − 30 − 1.5000 − 2.0182 | 18.4818 |
| Tax | 25% × 18.4818 | 4.6205 |
| Debt | fully repaid in month 30, so drawdown, interest, repayment | 0 |
| Project CF = Equity CF | 0.4167 − 0.0083 − 4.6205 | **−4.2121** |

### 6.5 NPV sum

Equity CF per month is read from workbook column P (rounded to 4 decimals). DF = 1 ÷ 1.011715^t to 6
decimals. PV = CF × DF to 4 decimals. A person checking this should spot-check at least months 1, 8, 12,
24, 30 and 36 and then sum the column.

| Month | Equity CF | DF | PV |
|---|---|---|---|
| 1 | -10.5000 | 0.988421 | -10.3784 |
| 2 | -0.6050 | 0.976975 | -0.5911 |
| 3 | -0.6100 | 0.965663 | -0.5891 |
| 4 | -0.1752 | 0.954481 | -0.1672 |
| 5 | -0.2901 | 0.943429 | -0.2737 |
| 6 | -0.3970 | 0.932504 | -0.3702 |
| 7 | -0.1958 | 0.921707 | -0.1805 |
| 8 | -0.0834 | 0.911034 | -0.0760 |
| 9 | 0.0395 | 0.900485 | 0.0356 |
| 10 | 0.1728 | 0.890058 | 0.1538 |
| 11 | 0.3166 | 0.879751 | 0.2785 |
| 12 | 0.4711 | 0.869564 | 0.4097 |
| 13 | 0.6363 | 0.859495 | 0.5469 |
| 14 | 0.6123 | 0.849543 | 0.5202 |
| 15 | 0.5972 | 0.839706 | 0.5015 |
| 16 | 0.5909 | 0.829983 | 0.4904 |
| 17 | 0.5937 | 0.820372 | 0.4871 |
| 18 | 0.6056 | 0.810873 | 0.4911 |
| 19 | 0.6266 | 0.801483 | 0.5022 |
| 20 | 0.6570 | 0.792203 | 0.5205 |
| 21 | 0.6967 | 0.783029 | 0.5455 |
| 22 | 0.7459 | 0.773962 | 0.5773 |
| 23 | 0.8046 | 0.765000 | 0.6155 |
| 24 | 0.8730 | 0.756142 | 0.6601 |
| 25 | 1.1163 | 0.747387 | 0.8343 |
| 26 | 2.1373 | 0.738732 | 1.5789 |
| 27 | 2.3111 | 0.730178 | 1.6875 |
| 28 | 2.5031 | 0.721723 | 1.8065 |
| 29 | 2.7135 | 0.713366 | 1.9357 |
| 30 | 2.9421 | 0.705106 | 2.0745 |
| 31 | 2.4500 | 0.696941 | 1.7075 |
| 32 | 2.0417 | 0.688871 | 1.4065 |
| 33 | 1.6333 | 0.680894 | 1.1121 |
| 34 | 1.2250 | 0.673010 | 0.8244 |
| 35 | 0.8167 | 0.665217 | 0.5433 |
| 36 | -4.2121 | 0.657514 | -2.7695 |
| **Sum** | | | **7.4514** |

### 6.6 Results

| Check | Hand value | Tool value | Difference | Done by | Date | Re-performed by Surya |
|---|---|---|---|---|---|---|
| Month 1 equity CF | −10.5000 | −10.5000 | 0 | Claude Code (calculator-style) | 2026-11-05 | ☐ |
| Month 8 equity CF | −0.0834 | −0.0834 | 0 | Claude Code (calculator-style) | 2026-11-05 | ☐ |
| Month 36 equity CF | −4.2121 | −4.2121 | 0 | Claude Code (calculator-style) | 2026-11-05 | ☐ |
| NPV sum | 7.4514 | 7.4515 | −0.0001 (rounding of 36 PVs to 4 decimals) | Claude Code (calculator-style) | 2026-11-05 | ☐ |
| Break-even price, NPV = 0 | 6,249.5 | 6,249.6 | 0.1 (bisection tolerance ₹0.5) | Bisection through the workbook's own formulas, 13 LibreOffice recalculations | 2026-11-05 | ☐ Goal Seek |
| Cost-covering price, profit = 0 | 5,686.5 | 5,686.3 | 0.2 (bisection tolerance ₹0.5) | Same, 12 recalculations | 2026-11-05 | ☐ Goal Seek |

The bisection values are written in Summary!B21 and B22 of the workbook with a note in column C. To
re-perform: Data → Goal Seek (Excel) or Tools → Goal Seek (LibreOffice), set cell Summary!B2 to value 0 by
changing cell Inputs!B13; then set Summary!B14 to 0 by changing Inputs!B13. Overwrite B21 and B22 with the
Goal Seek results and replace the note.

Two small differences are expected and are not errors: the repayment in month 8 is 0.5209 by calculator
(50% × 1.0417 rounded) against 0.5208 in the exact engine, and the NPV sum is 7.4514 against 7.4515
because 36 products were each rounded to 4 decimals. Both are below ₹0.0002 crore.

## 7. Discrepancies found during development and how each was resolved

| # | Discrepancy | Root cause | Resolution | Evidence |
|---|---|---|---|---|
| 1 | Tool reported IRR as "None" for the base case although NPV was clearly positive | AI-written bisection used a bracket of −99% to +1000% per month; the final negative tax flow made NPV negative at both ends, so no sign change was found | Replaced with a grid scan from −50% to +100% per month, then bisection. Test added: IRR equals the discount rate at the break-even price | `tests/test_model.py` |
| 2 | Loan almost unused: peak debt ₹0.79 crore, interest ₹0.04 crore | First design funded only construction with debt; collections began before construction peaked and the sweep repaid the loan at once | Loan now funds a share of land, approval and construction spend. Peak debt ₹12.08 crore, interest ₹2.02 crore | AI log entry 7 |
| 3 | Excel IRR() returned #N/A in the downside case while the tool gave 13.3% | Excel's Newton iteration from the default 10% per period guess did not converge | Workbook formula now `=IRR(range, 0.01)`. Recalculated value matches the tool to 1e−12 | `benchmark/compare_cases.py` |
| 4 | Heavy-debt case: tool IRR −13.8%, Excel IRR 839%, NPV +₹8.68 crore | The equity cash flow changes sign twice (bullet repayment in month 36), so two rates give NPV = 0. Both answers are "correct" roots; neither is a usable IRR | Tool now counts roots in the plausible band and checks that IRR vs hurdle agrees with the NPV sign. If not, the KPI is flagged and a warning tells the user to decide on NPV. Comparison script treats such IRRs as informational | `feasibility/metrics.py` |
| 5 | Sensitivity table rendered 15 columns, mostly empty | Step labels differed by driver type (%, months, percentage points), so the pivot produced a column per label | Positional columns (−2 steps to +2 steps) plus a Step column stating the step size | `tests/test_edge_cases.py` |
| 6 | Memo number check flagged "16.7%" in the template memo | The price cushion was computed inside the memo and was not in the fact sheet | Cushion added to the fact sheet so the LLM also receives it | `tests/test_edge_cases.py` |
| 7 | Tornado chart coloured bars by input direction, so for cost drivers orange marked the favourable side | Legend logic assumed "higher input = favourable" | Bars now coloured by the direction of the metric: orange falls, blue rises | Screenshot review |
| 8 | Property test asserted NPV always falls when the discount rate rises; 5 random cases violated it | The assertion is only true for profitable projects with conventional cash flows. Reversed or multi-sign patterns and loss-making projects behave differently | Test restricted; the model was right | `tests/test_properties.py` |
| 9 | A single input change took 27.7 s in the browser | Sensitivity, tornado and scenario loops each ran the full appraisal including two break-even bisections | Break-even solving skipped inside loops; 1.7 s per change | `tests/ui_test.py` check 24 |
| 10 | LibreOffice reported success but wrote no file | Snap-packaged LibreOffice cannot write to /tmp | Recalculation folder moved inside the project | `benchmark/compare.py` |

## 8. Conclusion

Every cash flow figure the tool produces for the base case and for three further cases agrees with
an independently recalculated spreadsheet and with an exact-arithmetic recomputation to better than
1e−11. The one metric that genuinely disagreed between engines, equity IRR in a heavy-debt case, was
not an arithmetic error but the known non-uniqueness of IRR, and the tool now detects and flags it.
The hand calculation and Goal Seek steps in section 6 remain to be completed and signed by the team.
