# User Manual: Real Estate Project Feasibility and Financial Appraisal Tool

CE725 Construction Economics and Finance, IIT Bombay. Course Project, Topic 2. Version 1.1, 5 November 2026.
Team: Maneesha (Project Lead and Finance Modeller), Dinesh Sai (Data Lead), Sujay (AI and Tool Developer),
Surya Theja (Validation Engineer), Akshitha (Documentation and Reflection Lead).
A longer version with worked explanations of every screen is in `docs/USER_MANUAL_EXTENDED.md`.

## 1. Purpose and intended users

The tool answers one question: is this real estate project worth committing land and approval money to,
and how fragile is that answer? You enter land, construction, approval, sales, financing and tax
assumptions. The tool builds a month-by-month cash flow, computes equity NPV, equity and project IRR,
payback, profit on cost and the break-even selling price, and shows how each result moves when one
assumption changes.

- **Developers and promoters** deciding whether to buy land: use the verdict, peak equity requirement and break-even price.
- **Lenders and investors** judging downside resilience: use project IRR, the debt schedule, the tornado chart and the scenarios.
- **Directors and non-technical readers**: use the plain-language investment memo.

Every number on screen is reproducible from the monthly table and from the companion Excel workbook. The
tool is a decision-support aid, not a substitute for professional appraisal; section 7 lists what it does
not model.

## 2. Installation and launch

Needs Python 3.10 or newer; no internet except for the optional Claude memo.

```bash
python3 -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                   # opens http://localhost:8501
```

Press Ctrl+C in the terminal to stop. To check the installation run `pytest -q`; 383 tests should pass.

**Optional Claude memo.** Put an API key in `.streamlit/secrets.toml` as `AIML_API_KEY = "..."` (AIML API
gateway) or `ANTHROPIC_API_KEY = "..."` (Anthropic direct), or paste it into the field on the memo tab. The
secrets file is excluded from version control; a pasted key is held in memory only.

## 3. The screen and the inputs

Inputs are in the sidebar on the left in five groups, with a **Reset to benchmark base case** button at the
top. The verdict line and two rows of headline metrics sit at the top of the main area, and six tabs below
hold the detail: Summary, Cash flow, Sensitivity, Scenarios, Investment memo, Assumptions and validation.
Every input change recalculates the whole page in about two seconds. Money is in ₹ crore, areas in sq ft,
time in months from project start (month 1 is the first month).

| Group | Input | Unit | Base case | Meaning |
|---|---|---|---|---|
| Timeline and land | Minimum horizon | months | 36 | Model length; extended automatically if collections run later |
| | Land cost; payment month | ₹ crore; month | 20.00; 1 | One lump-sum payment |
| | Approval costs; from, to month | ₹ crore; months | 3.00; 1 to 3 | Spread evenly over the window |
| Construction | Saleable area | sq ft | 1,00,000 | Drives construction cost and revenue |
| | Construction cost | ₹/sq ft | 3,000 | × area = ₹30 crore |
| | Construction starts, ends | month | 4 to 30 | Spend follows an S-curve |
| Sales and collections | Selling price | ₹/sq ft | 7,500 | × area = ₹75 crore gross revenue |
| | Launch, sold out by | month | 7 to 30 | Area booked evenly across the window |
| | Collected at booking; balance over | %; months | 20; 6 | Rest arrives in equal monthly instalments |
| | Marketing and brokerage | % of collections | 2.0 | Paid when cash is collected |
| Financing | Loan share of spend | % | 50 | Of each month's land, approval and construction spend |
| | Interest rate | % p.a. nominal | 12.0 | Opening balance × rate ÷ 12, paid in cash monthly |
| | Collections swept to repayment | % | 50 | Residual repaid as a bullet in the final month |
| Tax and appraisal | Income tax on project profit | % | 25 | Paid in the final month |
| | Discount rate | % p.a. effective | 15.0 | Monthly rate = (1 + r)^(1/12) − 1 |

**Input rules.** End months must not precede start months, percentages must lie in 0 to 100, months must be
1 or more. A broken rule shows a red message naming the input and stops the calculation. **Horizon.** You set
a minimum only; if the last sale is in month 30 with 6 instalments, the model uses 36 months so no revenue is
lost. The horizon used is shown in the second metric row.

## 4. Reading the results

The verdict is **Viable** when equity NPV is positive at the discount rate. The other metrics say how
comfortable the margin is. Base-case values let you check your installation.

| Metric | Base case | How it is computed | How to read it |
|---|---|---|---|
| Equity NPV | ₹7.45 cr | Σ equity CF ÷ (1 + m)^t, month 1 discounted one full month (Excel NPV convention) | Positive: earns more than the hurdle after funding costs |
| Equity IRR | 47.2% p.a. | Monthly rate giving zero equity NPV, annualised (1 + i)^12 − 1 | Compare with the discount rate |
| Project IRR | 34.2% p.a. | Same on the unlevered project cash flow | The lender's view of the project itself |
| Payback | 27 months | First month cumulative equity CF reaches zero | How long promoters' money is at risk |
| Profit on cost | 32.7% pre-tax | (Revenue − total cost incl. interest) ÷ total cost | The developer's margin; post-tax on the Summary tab |
| Break-even price | ₹6,250/sq ft | Price at which equity NPV = 0, by bisection | Price cushion before the hurdle is missed |
| Cost-covering price | ₹5,686/sq ft | Price at which pre-tax profit = 0 | Below this the project loses money |
| Peak equity requirement | ₹12.86 cr, month 8 | Most negative cumulative equity CF | Cash the promoters must have, and when |
| Peak debt; total interest | ₹12.08 cr; ₹2.02 cr | Highest closing loan balance; Σ interest | Facility size; cost of leverage |

**Cautions.** IRR shows n/a when cash flows never change sign or no rate between −50% and +100% per month
gives zero NPV. If the equity cash flow changes sign more than once (typically a large bullet repayment)
more than one IRR exists; the tool marks the IRR with a warning and you should decide on NPV alone. A high
equity IRR with a thin NPV usually means a small equity base, not a safe project.

**Cash flow tab.** One row per month, inflows positive and outflows negative: land, approvals,
construction, marketing, sales booked, collections, tax, project CF, the loan schedule (opening, drawdown,
interest, repayment, closing), equity CF and cumulative equity CF. Project CF = collections − spend − tax;
equity CF = project CF + drawdown − interest − repayment. **Download cash flow (CSV)** exports the table
for an independent check.

## 5. Sensitivity, tornado and scenarios

**One-at-a-time table.** Each row changes a single input and holds the rest: price and the three costs at
−20% to +20%, sales launch and construction delay at −6 to +6 months, interest and discount rate at −2 to
+2 percentage points. Radio buttons switch the metric between equity NPV, equity IRR, project IRR and
profit on cost.

**Tornado chart.** Bars show the metric at ±10% for prices and costs, ±3 months for delays, ±2 points for
rates, widest bar at the top. Orange is the side where the metric falls, blue where it rises. In the base
case the order is selling price, construction cost, sales launch delay, land cost.

**Scenarios.** Downside: price −10%, construction cost +10%, launch delayed 6 months (NPV −₹1.88 cr).
Severe downside: price −20%, cost +15%, launch delayed 12 months, interest +2 points (NPV −₹11.01 cr).
Upside: price +10%, cost −5%, launch 3 months earlier (NPV ₹14.98 cr). Five sliders build a custom case;
the chart compares its cumulative equity cash flow with the base case.

## 6. Investment memo

The memo is a one-page note in seven parts: recommendation, the project, funding, cushion and break-even,
key risk drivers, stress test, limitations. **Template mode** (default, offline) fills fixed sentences with
the computed numbers and is fully deterministic; use it for any figure that will be quoted. **Claude mode**
sends only the fact sheet shown in the expander (inputs, results, tornado and scenario figures) to a
Claude model through the AIML API gateway or Anthropic directly, and asks for plain language. The tool then
checks every number in the reply against the fact sheet and lists any that do not match in a yellow
warning; green means all matched. A matched number can still sit in the wrong sentence, so the memo is a
draft: read it against the metric rows before sending it. The person who signs the memo owns the numbers.
Do not use Claude mode for a confidential project unless the organisation permits sending the fact sheet
to a third party.

## 7. Key assumptions, data sources and limitations

**Conventions** (the engine and the workbook both follow them; any hand check must too):

1. Every cash flow occurs at the end of its month; PV = CF ÷ (1 + m)^t with m = (1 + annual)^(1/12) − 1 (1.1715% for 15%).
2. Land is one payment in the land month; approvals are spread equally across the approval window.
3. Construction follows a smoothstep S-curve: cumulative share after k of D months is 3x² − 2x³ with x = k ÷ D.
4. Sales are booked in equal value each month; each booking collects the booking share immediately and the balance in equal instalments; marketing is a share of each month's collections.
5. Drawdown = loan share × that month's land, approval and construction spend. Interest = opening balance × rate ÷ 12, paid in cash, not capitalised. Repayment = min(opening + drawdown, sweep × collections); any residual is a bullet in the final month.
6. Tax = rate × (revenue − land − approvals − construction − marketing − interest), paid in the final month, zero if profit is negative.
7. Profit on cost = pre-tax profit ÷ total development cost including interest. Break-even prices are found by bisection between ₹1 and four times the entered price with all else fixed.
8. Horizon = the longest of the minimum entered, last sale month plus instalment months, construction end, approval end and land month.

**Where the base case comes from.** It represents a mid-segment project of 1,00,000 sq ft in the
peripheral Mumbai Metropolitan Region (Kalyan-Dombivli or Panvel). Each input was checked against published
sources on 5 November 2026; the full table with links is `docs/DATA_SOURCES.md`.

| Input | Base case | Published reference |
|---|---|---|
| Selling price | ₹7,500/sq ft | Knight Frank H2 2025: Mumbai average ₹8,856; Panvel average ₹7,835; Kalyan registered rate ₹7,900 |
| Construction cost | ₹3,000/sq ft | Mumbai standard quality ₹3,086 (Oct 2026); JLL 2026 commercial high-rise ₹3,900 to 4,900 |
| Land cost | ₹20 cr | JLL: MMR transacted land about ₹17 cr per acre in 2024 |
| Approval costs | ₹3 cr | MCHI: 23% to 32% of project cost inside Greater Mumbai; far lower outside BMC limits |
| Interest rate | 12% | RBI repo 5.50% (Oct 2026); NBFC construction finance 11% to 14% |
| Tax; discount rate | 25%; 15% | Section 115BAA 25.17%; EY/NSE 2024 real estate cost of equity 16.4% |
| Booking 20%, 6 instalments | | RERA s.13 caps the pre-agreement advance at 10%; construction-linked plans run 18 to 30 months |

Three inputs lean optimistic for Mumbai: the 6-month instalment pattern, 2% marketing, and the approval cost
if the site is inside Greater Mumbai. They were kept so the validated benchmark stays intact; a real
appraisal should replace them with site-specific figures.

**Not modelled.** Inflation and price growth; GST, stamp duty and RERA escrow rules; unsold inventory,
cancellations and defaults; interest capitalisation, fees, moratoria and lender covenants; phased launches
or mixed unit prices; depreciation, loss carry-forward and MAT; probability distributions (sensitivities
are one-at-a-time, scenarios are hand-picked). A construction delay only stretches the S-curve, with no
overhead or escalation cost, so a pure construction delay can raise NPV slightly (+₹0.36 cr for 3 months in
the base case); read that as a model limitation, not a benefit of delay.

**Validation.** `benchmark/base_case_benchmark.xlsx` rebuilds the base case in plain formulas with no value
copied from Python; `python benchmark/compare.py` recalculates it and prints a discrepancy table. Goal Seek
on Summary!B2 (NPV) and B14 (profit), changing Inputs!B13 (price), reproduces the two break-even prices.
The hand calculation of months 1, 8 and 36 and the NPV sum is in section 6 of the validation report.

**Troubleshooting.**

| Symptom | Cause | Fix |
|---|---|---|
| Red message, no results | An input rule is broken | Correct the named input |
| IRR n/a or marked with a warning | No sign change, or more than one sign change in the equity cash flow | Decide on NPV; raise the sweep to shrink the bullet repayment |
| Break-even price n/a | No price up to four times the entered one gives zero NPV | Lower costs; the project is far from viable |
| Claude memo fails, or yellow number warning | No key, no internet, rate limit; or the model used a figure not in the fact sheet | Use template mode; check each listed number against the metric rows |
| Workbook differs from the app | Not recalculated, or an input differs | Press Reset in the app; force recalculation (Ctrl+Shift+F9) |

For questions about the model contact the Project Lead and Finance Modeller; for installation problems the
AI and Tool Developer.
