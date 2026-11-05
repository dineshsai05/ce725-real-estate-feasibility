# LLM memo test - anthropic/claude-sonnet-5-5 via AIML API

Generated 2026-11-05 17:28 from the base-case fact sheet. Time 12.2s. Number-check warnings: 0.

## Warnings

None: every number in the memo appears in the fact sheet.

## Memo text (verbatim, unedited)

Investment Memo

1. Recommendation
Proceed, with caution. At the 15% required return, the project is viable. Equity NPV (today's value of the cash left for the developer after meeting the 15% return) is ₹7.45 cr. The equity IRR (annualised return on the developer's own money) is 47.2%. However, the downside scenario turns the NPV negative, so selling price and timing need active management.

2. The project
The project has 100,000 sq ft to sell at ₹7,500 per sq ft, for gross revenue of ₹75.00 cr. Land costs ₹20.00 cr, construction ₹30.00 cr and approvals ₹3.00 cr. Total development cost is ₹56.52 cr, including ₹2.02 cr of interest. Pre-tax profit is ₹18.48 cr, a 32.7% profit on cost before tax and 24.5% after tax. Sales launch in month 7 and are complete by month 30.

3. Funding
Debt covers 50% of land, approval and construction spend at 12% a year, and 50% of customer collections go to repaying it. Peak debt is ₹12.08 cr and is fully repaid in month 30. Peak equity need is ₹12.86 cr, in month 8. Equity is paid back in 27 months, or 28 months once the 15% return is factored in.

4. Cushion and break-even
The selling price can fall to ₹6,250 per sq ft before NPV hits zero, which is a 16.7% cushion. To cover all costs with no profit, the price would need to be ₹5,686 per sq ft.

5. Key risk drivers
Ranked by impact on equity NPV:
- Selling price matters most. A 10% fall cuts NPV to ₹2.98 cr, and a 10% rise lifts it to ₹11.95 cr.
- Construction cost comes next. A 10% rise cuts NPV to ₹5.52 cr.
- A three-month delay in sales launch cuts NPV to ₹5.81 cr.
- A 10% rise in land cost cuts NPV to ₹5.88 cr.
- Interest rate, discount rate and approval cost have modest effects. For example, interest rates 2 percentage points higher leave NPV at ₹7.21 cr.
- A three-month construction delay shows NPV of ₹7.82 cr, slightly higher than the base case. This is probably because spending is pushed later. It should not be read as a benefit, since delays usually bring other costs that this model may not capture.

6. Stress test
- Upside: NPV ₹14.98 cr, equity IRR 109.7%, payback 18 months, peak equity ₹11.71 cr.
- Downside: NPV falls to -₹1.88 cr, equity IRR to 9.7% (below the 15% hurdle), payback stretches to 37 months and peak equity rises to ₹19.25 cr.
- Severe downside: NPV is -₹11.01 cr, equity IRR is -10.1%, equity is never paid back (payback not available) and peak equity reaches ₹27.27 cr.

In weaker cases the developer must put in much more equity, and the return disappears.

7. Limitations
The fact sheet does not say which assumptions were changed in the downside, severe and upside scenarios, so I cannot say how likely they are. The results rest on a single set of inputs for price, cost and absorption. Anything not in the fact sheet, such as other taxes or financing conditions, is not covered here. Lenders should confirm the equity commitment can stretch toward the downside peak of ₹19.25 cr before committing.

## Fact sheet sent

```
PROJECT INPUTS
- Saleable area: 100,000 sq ft
- Selling price: ₹7,500 per sq ft; gross revenue ₹75.00 cr
- Land cost: ₹20.00 cr paid in month 1
- Construction cost: ₹3,000 per sq ft = ₹30.00 cr, months 4 to 30
- Approval costs: ₹3.00 cr
- Sales: launch month 7, sold out by month 30; 20% on booking, balance over 6 months
- Debt: 50% of land, approval and construction spend at 12% p.a.; 50% of collections swept to repayment
- Income tax 25%; discount rate 15% p.a.
- Project horizon: 36 months

RESULTS
- Verdict at 15% hurdle: VIABLE
- Equity NPV: ₹7.45 cr
- Equity IRR: 47.2%; Project (unlevered) IRR: 34.2%
- Payback (equity): 27 months (2.2 years); discounted payback: 28 months (2.3 years)
- Total development cost: ₹56.52 cr (incl. interest ₹2.02 cr)
- Pre-tax profit: ₹18.48 cr; profit on cost 32.7% pre-tax, 24.5% post-tax
- Break-even selling price (NPV = 0): ₹6,250 per sq ft; price cushion 16.7% below the assumed price
- Cost-covering selling price (profit = 0): ₹5,686 per sq ft
- Peak equity requirement: ₹12.86 cr in month 8
- Peak debt: ₹12.08 cr; debt fully repaid in month 30

SENSITIVITY (equity NPV, ₹ cr) - most influential first
- Selling price: -10% -> 2.98; +10% -> 11.95
- Construction cost: -10% -> 9.39; +10% -> 5.52
- Sales launch delay (months): -3 mo -> 9.28; +3 mo -> 5.81
- Land cost: -10% -> 9.03; +10% -> 5.88
- Discount rate (abs. change): -2 pp -> 8.15; +2 pp -> 6.79
- Construction delay (months): -3 mo -> 7.09; +3 mo -> 7.82
- Interest rate (abs. change): -2 pp -> 7.69; +2 pp -> 7.21
- Approval cost: -10% -> 7.68; +10% -> 7.22

SCENARIOS
- Base case: NPV 7.45 cr, equity IRR 47.2%, payback 27.0 months, peak equity 12.86 cr
- Downside: NPV -1.88 cr, equity IRR 9.7%, payback 37.0 months, peak equity 19.25 cr
- Severe downside: NPV -11.01 cr, equity IRR -10.1%, payback nan months, peak equity 27.27 cr
- Upside: NPV 14.98 cr, equity IRR 109.7%, payback 18.0 months, peak equity 11.71 cr
```
