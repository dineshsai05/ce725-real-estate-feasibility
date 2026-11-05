# User Manual: Real Estate Project Feasibility and Financial Appraisal Tool

CE725 Construction Economics and Finance, IIT Bombay. Course Project, Topic 2.
Version 1.0, 30 October 2026.

Team: Maneesha (Project Lead and Finance Modeller), Dinesh Sai (Data Lead), Sujay (AI and Tool Developer),
Surya Theja (Validation Engineer), Akshitha (Documentation and Reflection Lead).

---

## 1. Purpose and intended users

The tool answers one question: is this real estate project worth committing land and approval money to,
and how fragile is that answer? You enter land, construction, approval, sales, financing and tax
assumptions. The tool builds a month-by-month cash flow, computes equity NPV, equity and project IRR,
payback, profit on cost and the break-even selling price, and then shows how each result moves when one
assumption changes.

It is built for three readers.

- **Developers and promoters** deciding whether to buy land and start approvals. Use the headline verdict,
  the peak equity requirement and the break-even price.
- **Lenders and investors** judging downside resilience. Use the project IRR, the debt schedule, the
  tornado chart and the stress scenarios.
- **Directors and non-technical decision-makers** who receive the plain-language investment memo without
  opening the model.

Every number on screen is reproducible from the monthly cash flow table and from the companion Excel
workbook, so a user can audit any figure by hand. The tool is a decision-support aid, not a substitute for
professional appraisal; see section 11 for what it does not model.

## 2. Installation and launch

The tool runs locally in a web browser. It needs Python 3.10 or newer and about 300 MB of disk space for
its libraries. No internet connection is needed except for the optional Claude memo.

1. Unzip or clone the project folder and open a terminal inside it.
2. Create a virtual environment and install the dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. A browser tab opens at http://localhost:8501. If it does not, copy that address into any browser.
5. To stop the app, press Ctrl+C in the terminal.

**Optional Claude memo.** To draft the investment memo with Claude instead of the built-in template you
need an API key from one of two providers: the AIML API (a third-party gateway that serves Claude and other
models through an OpenAI-compatible endpoint) or Anthropic directly. Put the key in `.streamlit/secrets.toml`
as `AIML_API_KEY = "..."` or `ANTHROPIC_API_KEY = "..."` (this file is excluded from version control), set it
as an environment variable of the same name, or paste it into the field on the Investment memo tab. A pasted
key is held in memory for the session only and is never written to disk.

**Checking the installation.** Run `pytest -q` in the project folder. Ten tests should pass. They check
the NPV and IRR functions against hand-worked examples and confirm the model identities listed in
section 9.

## 3. The screen at a glance

The page has three zones. Inputs are on the left, the headline results are at the top of the main area,
and the detail lives in six tabs below them. Every change to an input recalculates everything on the page
immediately.

| Zone | What it holds | What to do there |
|---|---|---|
| Sidebar (left) | Five input groups: Timeline and land, Construction, Sales and collections, Financing, Tax and appraisal. A **Reset to benchmark base case** button at the top. | Type or step values. Press Reset to return every input to the validated base case. |
| Verdict line | "Viable" or "Not viable" at the chosen hurdle rate. | Read first. Viable means equity NPV is positive at the discount rate. |
| KPI row 1 | Equity NPV, equity IRR, payback, profit on cost (pre-tax), break-even price. | The five metrics the course brief asks for. |
| KPI row 2 | Project IRR, peak equity requirement, peak debt, total interest, horizon used. | Funding and lender view. Hover the small help icons for the month in which each peak occurs. |
| Tab: Summary | Cost breakdown bar chart, revenue and profit table, cumulative S-curves. | The one-screen story of the project. |
| Tab: Cash flow | Monthly inflow and outflow bars, debt schedule chart, full monthly table, CSV download. | Audit any number. |
| Tab: Sensitivity | One-at-a-time table and tornado chart for a chosen metric. | Find which assumption matters most. |
| Tab: Scenarios | Preset downside, severe and upside cases plus five custom stress sliders. | Stress test the decision. |
| Tab: Investment memo | Template memo or Claude-drafted memo, with the fact sheet it was built from. | Produce the one-page note for a director. |
| Tab: Assumptions and validation | Numbered modelling conventions, benchmark workbook download, inputs download. | Check what the model assumes and run the validation. |

Money is always in rupees crore (1 crore = 10,000,000). Areas are in square feet. Time is in months
counted from project start, and month 1 is the first month.

## 4. Entering inputs

All 21 inputs are listed below with the base case value. The base case is the validated benchmark; start
from it and change one thing at a time so you can see the effect.

| Group | Input | Unit | Base case | Meaning |
|---|---|---|---|---|
| Timeline and land | Minimum horizon | months | 36 | Length of the model. Extended automatically if sales or collections run later. |
| Timeline and land | Land cost | ₹ crore | 20.00 | Paid as one lump sum. |
| Timeline and land | Land payment month | month | 1 | When the land is paid for. |
| Timeline and land | Approval and statutory costs | ₹ crore | 3.00 | Spread evenly over the approval months. |
| Timeline and land | Approvals from, to month | month | 1 to 3 | Window over which approval costs are paid. |
| Construction | Saleable area | sq ft | 1,00,000 | Area that is sold. Drives both construction cost and revenue. |
| Construction | Construction cost | ₹ per sq ft | 3,000 | Multiplied by saleable area gives total construction cost (₹30 crore). |
| Construction | Construction starts, ends month | month | 4 to 30 | Spend follows an S-curve: slow start, fast middle, slow finish. |
| Sales and collections | Selling price | ₹ per sq ft | 7,500 | Multiplied by saleable area gives gross revenue (₹75 crore). |
| Sales and collections | Launch month, sold out by month | month | 7 to 30 | Area is booked evenly across this window. |
| Sales and collections | Collected at booking | % | 20 | Share of each sale received in the month it is booked. |
| Sales and collections | Balance collected over | months | 6 | The rest arrives in equal monthly instalments after booking. |
| Sales and collections | Marketing and brokerage | % of collections | 2.0 | Paid in the month the cash is collected. |
| Financing | Loan share of spend | % | 50 | Share of each month's land, approval and construction spend drawn as loan. |
| Financing | Interest rate | % per year, nominal | 12.0 | Monthly interest = opening balance × rate ÷ 12, paid in cash each month. |
| Financing | Collections swept to repayment | % | 50 | Share of each month's collections used to repay the loan. Any residual is repaid in the final month. |
| Tax and appraisal | Income tax on project profit | % | 25 | Applied to total project profit and paid in the final month. |
| Tax and appraisal | Discount rate | % per year, effective | 15.0 | Hurdle rate for NPV. Converted to a monthly rate as (1 + r)^(1/12) − 1. |

**Input rules.** End months must not be earlier than start months, percentages must lie between 0 and
100, and every month number must be 1 or more. If a rule is broken the page shows a red message naming
the problem and stops calculating until it is fixed.

**Horizon.** You set a minimum horizon only. If the last sale is in month 30 and instalments run 6
months, the model needs 36 months to collect every rupee. If a scenario delays the launch, the horizon
grows so that no revenue is lost off the end of the table. The horizon actually used appears in the
second KPI row.

## 5. Reading the results

The verdict is Viable when equity NPV is positive at the discount rate. That single test drives the
recommendation; the other metrics tell you how comfortable the margin is. The base case results are shown
alongside each definition so you can check your installation.

| Metric | Base case | How it is computed | How to read it |
|---|---|---|---|
| Equity NPV | ₹7.45 crore | Sum of each month's equity cash flow divided by (1 + monthly rate)^month. Month 1 is discounted one full month, the same convention as Excel's NPV function. | Positive means the project earns more than the hurdle rate after funding costs. |
| Equity IRR | 47.2% per year | The monthly rate at which equity NPV is zero, annualised as (1 + monthly)^12 − 1. | Compare with the discount rate. Equity IRR exceeds project IRR when the loan costs less than the project earns. |
| Project IRR | 34.2% per year | Same calculation on the unlevered project cash flow, before any loan drawdown, interest or repayment. | The return of the project itself, independent of how it is financed. The figure a lender looks at. |
| Payback | 27 months | First month in which cumulative equity cash flow turns from negative to zero or above. A discounted payback is also computed. | How long the promoters' money is at risk. |
| Profit on cost (pre-tax) | 32.7% | (Gross revenue − total development cost) ÷ total development cost, where cost includes land, construction, approvals, marketing and interest. | The developer's margin. A post-tax version appears on the Summary tab. |
| Break-even price (NPV = 0) | ₹6,250 per sq ft | The selling price at which equity NPV is exactly zero, found by repeated bisection. | The delta under it shows how far price can fall before the project stops clearing the hurdle. |
| Cost-covering price (profit = 0) | ₹5,686 per sq ft | The selling price at which pre-tax profit is zero. Shown on the Memo tab. | Below this the project loses money outright. |
| Peak equity requirement | ₹12.86 crore in month 8 | The most negative value of cumulative equity cash flow. | The cash the promoters must have available, and when. |
| Peak debt | ₹12.08 crore | Highest closing loan balance in any month. | The facility size a lender must sanction. |
| Total interest | ₹2.02 crore | Sum of monthly interest payments. | The cost of leverage. |

Three cautions. IRR is reported as "n/a" when the cash flows never change sign or when no rate between
−50% and +100% per month gives zero NPV; in that case rely on NPV. If the equity cash flow changes sign
more than once (typically a large bullet repayment in the final month), more than one rate can give
zero NPV; the tool then marks the IRR with a warning sign, shows a yellow notice, and you should decide
on NPV alone. And a high equity IRR with a thin NPV usually means a small equity base, not a safe
project. Always read the break-even price and the peak equity figure together with the IRR.

## 6. Cash flow tab

This tab is the audit trail. Every headline figure can be traced to the monthly table shown here, and the
same table is what the Excel benchmark reproduces.

Inflows are positive and outflows are negative throughout. The table has one row per month and a Total
row at the bottom. Columns from left to right:

| Column | Content |
|---|---|
| Land, Approvals, Construction, Marketing | Development spend in the month, shown negative. |
| Sales booked | Value of area sold in the month. Not cash; it drives collections. |
| Collections | Cash received: the booking share of this month's sales plus instalments on earlier sales. |
| Tax | Income tax, in the final month only. |
| Project CF | Collections minus all development spend and tax. The unlevered cash flow. |
| Debt opening, Drawdown, Interest, Repayment, Debt closing | The loan schedule. Closing = opening + drawdown − repayment. Interest is paid in cash and does not accrue to the balance. |
| Equity CF | Project CF + drawdown − interest − repayment. The cash the promoters put in or take out. |
| Cum. equity CF | Running total of Equity CF. Its minimum is the peak equity requirement; the month it crosses zero is the payback. |

Two charts sit above the table. The left one stacks collections, development spend, and interest plus
tax by month, with net equity cash flow drawn as a line. The right one shows loan drawdown and repayment
with the closing balance as a line.

Use **Download cash flow (CSV)** to export the full table, including cumulative columns, for a report or
for an independent check in any spreadsheet.

## 7. Sensitivity, tornado and scenarios

The Sensitivity tab answers "which assumption should I worry about"; the Scenarios tab answers "what if
several go wrong at once".

**Choosing the metric.** The radio buttons at the top switch both the table and the tornado between
equity NPV, equity IRR, project IRR and pre-tax profit on cost.

**One-at-a-time table.** Each row changes a single input and holds every other input at its current
value. The columns are positional (−2 steps to +2 steps) and the first column states the step size for that row.

| Driver | Steps shown | Adverse direction |
|---|---|---|
| Selling price | −20%, −10%, 0, +10%, +20% | Lower |
| Construction cost, land cost, approval cost | −20%, −10%, 0, +10%, +20% | Higher |
| Sales launch delay | −6, −3, 0, +3, +6 months | Later. The whole sales window and the horizon shift together. |
| Construction delay | −6, −3, 0, +3, +6 months | Later. The S-curve stretches to the new end month. |
| Interest rate, discount rate | −2, −1, 0, +1, +2 percentage points | Higher |

**Tornado chart.** Each bar shows the metric at a fixed swing of the input: ±10% for prices and
costs, ±3 months for delays, ±2 percentage points for rates. Bars are sorted so the widest, meaning the
most influential input, is at the top. Orange marks the side where the metric falls and blue the side
where it rises; hover a bar to see which direction of the input produced it. In the
base case selling price is the widest bar, followed by construction cost, sales launch delay and land cost.

**Preset scenarios.** The table at the top of the Scenarios tab applies several changes together.

| Scenario | Changes applied |
|---|---|
| Base case | None |
| Downside | Price −10%, construction cost +10%, launch delayed 6 months |
| Severe downside | Price −20%, construction cost +15%, launch delayed 12 months, interest +2 percentage points |
| Upside | Price +10%, construction cost −5%, launch 3 months earlier |

**Custom stress test.** Five sliders let you set your own combination: price, construction cost, land
cost, launch delay and interest rate. The metrics update as you drag, and the chart below compares the
cumulative equity cash flow of your scenario with the base case. The delta under Equity NPV shows the
change against the current sidebar inputs.

## 8. Investment memo

The memo turns the model output into a one-page note for a director or lender who will not open the
tool. It has seven fixed parts: recommendation, the project, funding, cushion and break-even, key risk
drivers, stress test, limitations.

**Two ways to generate it.**

| Mode | How it works | When to use it |
|---|---|---|
| Template (offline, deterministic) | Fills fixed sentences with the computed numbers. Same inputs always give the same memo. No internet needed. | Default. Use for the demo and for any figure that will be quoted. |
| Claude (LLM) | Sends a fact sheet of the computed numbers to a Claude model, through the AIML API gateway or Anthropic's own API, and asks for the memo in plain language. Needs an API key. The default model is Claude Sonnet 5.5; any model name the provider accepts can be typed in. | When a more natural narrative is wanted and someone will check it. |

**What is sent to the API.** Only the fact sheet shown in the expander at the bottom of the tab: the
inputs, the results, the tornado figures and the scenario table. No file, no personal data and nothing
outside the fact sheet leaves the machine. The fact sheet is sent to Anthropic's servers, so do not use
Claude mode for a confidential project unless the organisation permits it.

**The number check.** After Claude replies, the tool extracts every number in the memo and looks for it
in the fact sheet. Numbers that are not found are listed in a yellow warning. A green message means every
number matched. A number can match and still be used in the wrong sentence, so the check reduces risk but
does not remove it.

**Your obligation.** The Claude memo is a draft. Read it against the KPI rows before sending it to
anyone. The course treats unverified AI output presented as the team's own analysis as misconduct, and
the same standard applies in practice: the person who signs the memo owns the numbers.

Type a project name in the field at the top so it appears in the heading. Both modes offer a text
download.

## 9. Validation with the benchmark workbook

The file `benchmark/base_case_benchmark.xlsx` rebuilds the base case in plain spreadsheet formulas. It
contains no value copied from the Python model, so a match between the two is evidence that the engine is
right. On 30 October 2026 the workbook, recalculated in LibreOffice Calc, matched the app on all 17
summary metrics to within 1e−11 and on every monthly cash flow column to within 5e−14 crore.

**What the workbook contains.**

| Sheet | Content |
|---|---|
| Inputs | The 21 inputs in yellow cells, plus three derived cells: total construction cost, gross revenue and the monthly discount rate. Change a yellow cell and the whole workbook recalculates. |
| CashFlow | One row per month with the same columns as the app's Cash flow tab, each a formula referring to Inputs. Extra helper columns show the cumulative S-curve share, a payback flag, the discount factor and the present value of each month's equity cash flow. |
| Summary | NPV via Excel's NPV function and again as the sum of the PV column, IRR via Excel's IRR function and its annualised value, payback, revenue, cost, profit, margins, peak debt and peak equity. Two yellow cells await the Goal Seek results. |

**How to compare.**

1. In the app, press Reset to benchmark base case and note the KPI rows.
2. Open the workbook in Excel or LibreOffice. Both recalculate on opening. Compare the Summary sheet with
   the KPI rows.
3. Or run `python benchmark/compare.py` in the project folder. It recalculates the workbook headlessly,
   reads the results and prints a discrepancy table with a Match column. The latest table is saved in
   `docs/validation_results.md`.

**Manual Goal Seek steps.** The break-even prices are deliberately left as manual work.

1. On the Summary sheet select the Equity NPV cell (B2). Use Data → What-If Analysis → Goal Seek (Excel)
   or Tools → Goal Seek (LibreOffice).
2. Set the cell to 0 by changing Inputs!B13, the selling price. Record the result in Summary!B21. The app
   shows ₹6,250 per sq ft.
3. Repeat with the Pre-tax profit cell (B14) set to 0, and record it in B22. The app shows ₹5,686 per
   sq ft.
4. Restore the selling price to 7,500 afterwards.

**Hand check.** The course requires a benchmark worked without AI. The validation engineer should
compute months 1, 8 and 36 of the cash flow by hand from the formulas in section 10, then the 36 discount
factors and the NPV sum, and record the comparison in the validation report. The workbook is a
cross-check with a different calculation engine; it is not that hand check.

## 10. Key assumptions

These are the conventions the engine and the workbook both follow. Any hand check must use the same ones
to match.

1. **Timing.** Every cash flow occurs at the end of its month. Month 1 is discounted one full month:
   PV = CF ÷ (1 + m)^t, where m is the monthly rate and t the month number.
2. **Discount rate.** The annual rate entered is effective. Monthly rate m = (1 + annual)^(1/12) − 1.
   For 15% this is 1.1715% per month.
3. **Land** is one payment in the land month. **Approvals** are spread equally across the approval window.
4. **Construction S-curve.** For a window of D months, the cumulative share spent by the end of the k-th
   month is 3x² − 2x³ with x = k ÷ D. The monthly spend is the difference between consecutive cumulative
   shares. Shares sum to exactly 1.
5. **Sales** are booked in equal value each month from launch to sold-out. Collections of each booking
   are the booking percentage in that month and the remainder in equal instalments over the following
   instalment months. Marketing is a percentage of the month's collections.
6. **Loan drawdown** each month equals the loan share multiplied by that month's land, approval and
   construction spend. **Interest** equals the opening balance multiplied by the annual rate divided by
   12 and is paid in cash the same month; it is not capitalised.
7. **Repayment** each month is the smaller of the available balance (opening plus drawdown) and the
   sweep percentage of that month's collections. Whatever remains in the final month is repaid as a
   bullet.
8. **Tax** equals the tax rate multiplied by total project profit, where profit is gross revenue less
   land, approvals, construction, marketing and interest. It is paid in the final month and is zero if
   profit is negative.
9. **Project cash flow** = collections − land − approvals − construction − marketing − tax.
   **Equity cash flow** = project cash flow + drawdown − interest − repayment. NPV and the headline IRR
   use equity cash flow; project IRR uses project cash flow.
10. **Profit on cost** divides pre-tax profit by total development cost including interest. The post-tax
    version subtracts tax from the numerator only.
11. **Break-even prices** are found by bisection on the selling price between ₹1 and four times the
    entered price, holding every other input fixed. Interest and tax change with price, so the result is
    not a simple ratio.
12. **Horizon** is the longest of: the minimum horizon entered, last sale month plus instalment months,
    construction end, approval end and land month.

**Where the base-case values come from.** The base case represents a mid-segment project of 1,00,000 sq ft
in the peripheral Mumbai Metropolitan Region (Kalyan-Dombivli or Panvel). Each input was checked against
published sources on 5 November 2026; the full table with links is in `docs/DATA_SOURCES.md`. In brief:

| Input | Base case | Published reference |
|---|---|---|
| Selling price | ₹7,500/sq ft | Knight Frank H2 2025: Mumbai average ₹8,856/sq ft; Panvel average ₹7,835; Kalyan registered rate ₹7,900 |
| Construction cost | ₹3,000/sq ft | Mumbai standard quality ₹3,086 (Oct 2026); JLL 2026 commercial high-rise ₹3,900 to 4,900 |
| Land cost | ₹20 cr | JLL: MMR transacted land about ₹17 cr per acre in 2024 |
| Approval costs | ₹3 cr | MCHI: 23% to 32% of project cost inside Greater Mumbai; far lower outside BMC limits |
| Interest rate | 12% | RBI repo 5.50% (Oct 2026); NBFC construction finance 11% to 14% |
| Tax rate | 25% | Section 115BAA: 25.17% |
| Discount rate | 15% | EY/NSE 2024 survey: real estate cost of equity 16.4% |
| Booking 20%, 6 instalments | | RERA s.13 caps the pre-agreement advance at 10%; real construction-linked plans run 18 to 30 months |

Three inputs lean optimistic for Mumbai (the 6-month instalment pattern, 2% marketing, and approval cost
if the site is inside Greater Mumbai). They were kept so that the validated benchmark stays intact; a real
appraisal should replace them with site-specific figures.

## 11. Known limitations and troubleshooting

The model is deliberately simple so that every figure can be checked by hand. That simplicity has costs,
and a user should know them before relying on the output.

**Not modelled.**

- Inflation, cost escalation and selling price growth over the sales window. All prices are flat in
  today's rupees.
- GST, stamp duty, registration charges and RERA escrow rules on collections.
- Unsold inventory. The model assumes the whole saleable area is sold within the sales window.
- Cancellations, payment defaults and collection delays beyond the fixed instalment pattern.
- Interest capitalisation, processing fees, a moratorium, lender covenants and minimum debt-service tests.
- Phased launches, multiple towers, or different prices for different unit types.
- Depreciation, loss carry-forward, minimum alternate tax and the timing of advance tax.
- Uncertainty. Sensitivities are one-at-a-time and scenarios are hand-picked; there is no probability
  distribution on the result.
- Collection timing. The instalment pattern (balance over a fixed number of months after booking) is
  simpler and faster than a MahaRERA construction-linked plan, where instalments follow slab milestones
  over 18 to 30 months. For a real project enter a longer instalment period, or model the plan explicitly.
- Delay penalties. A construction delay only stretches the spend S-curve; there is no overhead, idle-resource
  or escalation cost attached to it. Because later spend is discounted more, a pure construction delay can
  *raise* NPV slightly (base case: +₹0.36 cr for 3 months). Read that as a limitation of the model, not as a
  benefit of delay. A sales launch delay, by contrast, always hurts because it moves revenue later.

**Troubleshooting.**

| Symptom | Likely cause | Fix |
|---|---|---|
| Red error message and no results | An input rule is broken, for example an end month before a start month | Correct the named input. |
| IRR shows n/a | Cash flows never change sign, or no rate between −50% and +100% per month gives zero NPV | Use NPV. Check that revenue exceeds cost and that the horizon covers all collections. |
| IRR has a warning sign and a yellow notice | The equity cash flow changes sign more than once, so IRR is not unique or disagrees with the NPV sign | Decide on NPV. Reduce the final bullet repayment (raise the sweep) to see the IRR become unique again. |
| Break-even price shows n/a | No price between ₹1 and four times the entered price gives zero NPV | Lower costs or widen the price; the project is far from break-even either way. |
| Horizon used is longer than the minimum entered | Sales or instalments run past the minimum horizon | Expected. The horizon grows so no revenue is lost. |
| Claude memo fails with an error | No key, wrong key, no internet, or API rate limit | Use template mode, or set a valid key and retry. The error text names the cause. |
| Yellow warning listing numbers in the memo | The LLM used a figure not in the fact sheet | Check each listed number against the KPI rows before using the memo. |
| Workbook values differ from the app | Workbook not recalculated, or an input differs from the sidebar | Press Reset in the app and force a full recalculation (Ctrl+Shift+F9 in Excel). |
| `streamlit: command not found` | Virtual environment not activated | Run `source .venv/bin/activate` and try again. |

For questions about the model, contact the Project Lead and Finance Modeller. For installation problems,
contact the AI and Tool Developer.
