# Presentation and Live Demo Plan

15-minute demonstration followed by 5 minutes of questions. 31 October 2026. Evaluators move between
groups, so be ready to start at any moment and to restart from any point. Keep the app running
with the base case loaded and the Summary tab open.

## Before the session

- [ ] Laptop charged; charger packed.
- [ ] `source .venv/bin/activate && streamlit run app.py` tested once on the demo laptop. Browser zoom 110%.
- [ ] A second laptop or phone with the Excel workbook open at the Summary sheet.
- [ ] Printed: one-page cash flow table (base case), AI usage log, validation discrepancy table.
- [ ] Demo from the local app (`streamlit run app.py`) with the live link https://ce725-real-estate-feasibility.streamlit.app/ open in a second tab as backup; the cloud app sleeps after idle, so open it 5 minutes before.
- [ ] If demonstrating the Claude memo: `.streamlit/secrets.toml` present with `AIML_API_KEY`, internet checked, and one memo generated before the evaluators arrive (12 to 18 s). Otherwise use template mode and say why. Have `docs/llm_memo_claude-sonnet-5-5.md` open as a fallback.
- [ ] Every member can state every formula in section 10 of the user manual without notes.

## Demo script

| Minute | Speaker (role) | Screen | Say |
|---|---|---|---|
| 0 to 1 | Project Lead | Title and verdict line | The question a developer asks before buying land: is it viable, and how fragile is that answer. One sentence on the base case: 1 lakh sq ft, ₹7,500 per sq ft, ₹20 crore land, 36 months. |
| 1 to 3 | Project Lead | KPI rows | Walk the five course metrics: NPV ₹7.45 crore, equity IRR 47%, payback 27 months, 33% profit on cost, break-even ₹6,250. Then the second row: why equity IRR exceeds project IRR (leverage at 12% below a 34% project return), peak equity ₹12.9 crore in month 8. |
| 3 to 5 | Data Lead | Summary tab | Where the money goes bar chart. S-curves: spend leads collections by about 12 months, that gap is the funding need. Explain the smoothstep S-curve and why it was chosen (reproducible in Excel). State where each base-case number came from and what is an assumption. |
| 5 to 7 | Tool Developer | Cash flow tab | Point to month 8 in the table and read the row aloud: construction 0.925, collections 1.042, drawdown 0.463, interest 0.121, repayment 0.521. Show the debt chart. Show the CSV download. |
| 7 to 9 | Project Lead | Sensitivity tab | Tornado: price first, then construction cost, then sales delay, then land. Say the finding: a 3-month delay costs about as much as a 10% cost overrun. Switch the metric to Equity IRR to show the table updates. |
| 9 to 11 | Tool Developer | Scenarios tab | Preset downside: NPV turns negative at price −10%, cost +10%, delay 6 months. Drag one slider live. Then type 4,000 in the price box to flip the verdict and show the validation error by setting sold-out month to 5. Press Reset. |
| 11 to 13 | Validation Engineer | Excel workbook and Assumptions tab | Open the workbook Summary sheet beside the app: same NPV, IRR, payback to six decimals. Explain that the workbook has no Python values, only formulas. Describe the Goal Seek result and the hand check of months 1, 8 and 36. Mention the heavy-debt case where IRR was not unique and how the tool now warns. |
| 13 to 15 | Documentation Lead | Investment memo tab, AI log | Show the template memo and read the recommendation sentence. Show the fact sheet and explain the number check. Two AI errors from the log in one sentence each: the IRR bracket bug and the debt-on-construction-only design. Close: the AI built it with us, every number was checked against something it did not write. |

## Likely viva questions and short answers

Any member may be asked any of these. Answer with the formula, then the base-case number.

| Question | Answer |
|---|---|
| Where do the base-case numbers come from? | Mumbai Metropolitan Region periphery (Kalyan-Dombivli, Panvel). Each input is checked against a published source in `docs/DATA_SOURCES.md`: Knight Frank for price, JLL for land, MCHI for approvals, RBI and NBFC rate cards for interest, EY/NSE survey for the discount rate. Three inputs are optimistic and we say which. (Dinesh) |
| How do you convert the 15% annual discount rate to monthly? | Effective: (1.15)^(1/12) − 1 = 1.1715% per month. Not 15 ÷ 12 = 1.25%, which would be a nominal rate. |
| Why is month 1 discounted a full month? | End-of-month convention. Every flow in month t is divided by (1 + m)^t. It matches Excel's NPV() so the benchmark can use that function directly. |
| Define NPV and the decision rule. | Sum of discounted equity cash flows. Positive means the project earns more than the hurdle. Base case ₹7.45 crore. |
| Define IRR. When is it unreliable? | The rate at which NPV is zero, annualised as (1 + monthly)^12 − 1. Unreliable when the cash flow changes sign more than once (then there can be several roots) or when it conflicts with the NPV sign. Our heavy-debt test case had roots at −14% and 837%. |
| Why is equity IRR higher than project IRR? | Leverage. The project earns 34%; half the cost is borrowed at 12%. The spread accrues to the equity, which is smaller. Equity IRR 47%. If the loan rate exceeded the project return the order would reverse. |
| What is payback and its weakness? | First month cumulative equity cash flow reaches zero; 27 months. It ignores everything after that month and the time value of money. We also report discounted payback, 28 months. |
| What is profit on cost? | Pre-tax profit ÷ total development cost including interest: 18.48 ÷ 56.52 = 32.7%. Post-tax 24.5%. |
| How is the break-even price found? | Bisection on the selling price until equity NPV is zero: ₹6,250. Interest and tax change with price, so it is not a simple division. The cost-covering price (profit zero) is ₹5,686. |
| How is construction spend spread? | Smoothstep S-curve. Cumulative share after k of D months = 3(k/D)² − 2(k/D)³. Monthly spend is the difference of consecutive shares. Chosen because it is a single formula a spreadsheet can reproduce. |
| How are collections modelled? | 20% of each month's bookings immediately, the remaining 80% in 6 equal instalments over the next 6 months. Month 8 collections = 0.625 + 0.417 = 1.042 crore. |
| How does the loan work? | Drawdown = 50% of that month's land, approval and construction spend. Interest = opening balance × 12% ÷ 12, paid in cash. Repayment = min(balance, 50% of collections). Residual repaid in month 36. Peak ₹12.08 crore. |
| How is tax handled and why in the final month? | 25% of total project profit (revenue − land − approvals − construction − marketing − interest), paid in month 36. A simplification: real tax is paid in advance instalments on accounting profit. It makes the last cash flow negative, which is why IRR needs care. |
| What did the AI get wrong? | IRR bracket returning None; debt on construction only giving almost no interest; a false "NPV always falls with rate" test; inverted tornado colours; an unverified claim in the manual. All found by testing against something the AI did not write. |
| How did you validate? | Excel workbook of pure formulas recalculated in LibreOffice: all 17 metrics match to 1e−11. Three more input cases through the same formulas. An exact-decimal recomputation. 383 automated tests. Plus the hand calculation of months 1, 8, 36 by the Validation Engineer. |
| Would a developer use this? | For first screening, yes. For a real decision it needs escalation, GST, RERA escrow, phased launches, construction-linked collections and interest capitalisation. |
| What is the ethical risk? | Quoting an AI-generated number without checking it. The memo tab states that the person quoting the number owns it. The Claude mode sends data to an external API and the screen says so. |

## Slides (if slides are used; otherwise the app is the presentation)

1. Title, team, roles.
2. The question and the base case (one table).
3. Method: monthly cash flow, five metrics, assumptions list.
4. Live demo (switch to app).
5. Validation: four layers, discrepancy table.
6. What the AI got right and wrong (two columns).
7. Limitations and what real use needs.
