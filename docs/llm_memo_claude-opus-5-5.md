# LLM memo test - anthropic/claude-opus-5-5 via AIML API

Generated 2026-11-05 17:29 from the base-case fact sheet. Time 17.5s. Number-check warnings: 0.

## Warnings

None: every number in the memo appears in the fact sheet.

## Memo text (verbatim, unedited)

**Investment Memo: 100,000 sq ft Residential Development**

1. Recommendation

Proceed, subject to firm controls on pricing and sales timing. At the 15% hurdle rate (the minimum annual return we require), the model rates the project VIABLE. Equity NPV, the value created above that required return, is ₹7.45 cr. Equity IRR, the annual return on our own money, is 47.2%. The approval should still be conditional, because the downside scenarios turn negative.

2. The project

We would build and sell 100,000 sq ft at ₹7,500 per sq ft, for gross revenue of ₹75.00 cr. Land costs ₹20.00 cr, paid in month 1. Construction costs ₹30.00 cr, spent from month 4 to month 30, and approvals cost ₹3.00 cr. Total development cost is ₹56.52 cr, including ₹2.02 cr of interest. Pre-tax profit is ₹18.48 cr, which is 32.7% of cost before tax and 24.5% after tax. Sales launch in month 7 and the project is sold out by month 30.

3. Funding

Debt covers half of land, approval and construction spend at 12% a year. Half of all buyer collections go to repaying it. Peak debt is ₹12.08 cr, and the loan is fully repaid in month 30. Our own cash need peaks at ₹12.86 cr in month 8. We recover our equity in 27 months (2.2 years), or 28 months (2.3 years) once the time value of money is counted.

4. Cushion and break-even

Prices can fall to ₹6,250 per sq ft before NPV reaches zero, a cushion of 16.7% below plan. Prices would have to fall to ₹5,686 per sq ft before the project makes no profit at all.

5. Key risk drivers

Selling price matters most. A 10% price fall cuts NPV to ₹2.98 cr, and a 10% rise lifts it to ₹11.95 cr. The next biggest drivers are:
- **Construction cost:** a 10% overrun leaves NPV at ₹5.52 cr.
- **Sales launch timing:** a 3-month delay leaves NPV at ₹5.81 cr.
- **Land cost:** a 10% increase leaves NPV at ₹8.65 cr. Correction: the fact sheet gives ₹5.88 cr for a 10% land cost increase.

Interest rates and approval costs have only a minor effect.

6. Stress test

- **Downside scenario:** NPV turns negative at -₹1.88 cr. IRR falls to 9.7%, payback stretches to 37 months, and peak equity rises to ₹19.25 cr.
- **Severe downside:** NPV falls to -₹11.01 cr and IRR to -10.1%. No payback figure is reported, and peak equity reaches ₹27.27 cr.
- **Upside:** NPV rises to ₹14.98 cr with an IRR of 109.7%.

Under stress, the extra equity we would need is as important a risk as the lower returns.

7. Limitations

- The fact sheet does not define the downside, severe downside and upside scenarios, so their assumptions are not available.
- The model shows a 3-month construction delay *raising* NPV, from ₹7.09 cr to ₹7.82 cr. This runs against intuition and should be checked.
- The downside payback of 37 months is longer than the 36-month project horizon. The severe-case payback is reported as "nan", meaning no figure was produced.
- The individual cost items plus interest do not appear to add up to the stated total development cost. The fact sheet does not itemise the difference, so this should be confirmed with the modeller.
- No scenario probabilities, market sales evidence or cost contingency figures are available.

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
