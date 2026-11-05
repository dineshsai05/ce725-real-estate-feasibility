# Learnings and Reflection Report (DRAFT for the team to edit)

Real Estate Project Feasibility and Financial Appraisal Tool. CE725 Course Project, Topic 2.
Draft prepared 30 October 2026 with AI assistance. The team must rewrite this in its own words,
add the individual reflections, and check every claim. Sections follow the order required in the
course brief, section 7. Target length 10 to 15 pages.

## 1. Subject learnings

**A headline IRR hides the shape of the cash flow.** The base case shows an equity IRR of 47% and a
project IRR of 34%. The difference is leverage: half the development cost is borrowed at 12%, which is
below the project's return, so the equity earns more than the project does. The same leverage that
produces 47% also produces a ₹12.9 crore peak funding need in month 8 and ₹2 crore of interest. A
developer who looks only at IRR does not see either.

**Timing of sales matters as much as price.** In the tornado chart a 3-month delay in launch costs
almost as much NPV as a 10% rise in construction cost, and more than a 10% rise in land cost. Delay
costs money twice: collections arrive later, and the loan stays outstanding longer.

**NPV is the reliable decision measure; IRR is not always.** While testing a heavy-debt case we found
two rates at which NPV is zero (−14% and 837%). Excel found one, our code found the other, both were
mathematically correct, and neither was useful. The equity cash flow changed sign twice because of a
bullet repayment at the end. The tool now warns the user and tells them to decide on NPV. We had read
about multiple IRRs; we had not expected to produce one with realistic inputs.

**NPV does not always fall when the discount rate rises.** One of our automated tests asserted it
does. It failed for a loss-making project: when every cash flow nets to a loss, a higher rate shrinks
the loss and NPV rises toward zero. It also failed for cash flows with inflows first and outflows
later. The rule we learned in class holds for profitable, conventional projects only.

**Break-even has two meanings.** The price at which NPV is zero (₹6,250 per sq ft) and the price at
which the project merely covers its costs (₹5,686) differ by 10%. The gap is the return the equity
demands. Reporting only the second number would overstate how safe the project is.

**Conventions must be stated or two correct calculations disagree.** End-of-month discounting, an
effective versus nominal rate, interest on the opening or closing balance, and whether total cost
includes interest each change the answer. Our Excel and Python results matched only because both
followed one written assumptions list.

## 2. AI capability assessment

The AI (Claude Code) wrote almost all of the code and the first draft of every document. It was fast
and usually right, and it was wrong in specific ways that we caught only because we tested.

**Where it accelerated the work**
- The full cash flow engine, metrics, sensitivity module, Streamlit interface and Excel workbook
  generator were produced in one working session.
- It proposed the smoothstep S-curve (3x² − 2x³) precisely because it can be reproduced in a
  spreadsheet, which made the benchmark possible.
- It wrote 383 automated tests including 200 randomised input sets, far more than we would have
  written by hand.
- It explained its own errors clearly when asked.

**Where it was wrong, with evidence**

| # | Error | Type | How we found it |
|---|---|---|---|
| 1 | IRR function returned "None" for the base case | Faulty code: bisection bracket of −99% to +1000% per month had the same NPV sign at both ends | First run of the base case |
| 2 | Debt modelled on construction only, giving ₹0.04 crore of interest | Wrong assumption: did not consider that collections start before construction peaks | Reading the output and asking whether the numbers made sense |
| 3 | Asserted "NPV falls as the discount rate rises" as a universal test | Wrong finance assumption | Randomised tests failed on 5 of 40 cases |
| 4 | Sensitivity table with 15 mostly empty columns | Faulty code: labels per driver type created extra columns | A test on table shape |
| 5 | Tornado colours inverted for cost drivers | Faulty logic: coloured by input direction, not metric direction | Looking at a screenshot |
| 6 | Template memo contained a number (16.7%) not traceable to the fact sheet | Incomplete design | Its own number-check guard |
| 7 | Server restart command killed itself | Tooling error: pkill pattern matched its own shell | Empty test output |
| 8 | Wrote that land cost was the third-widest tornado bar in the manual | Fabricated ordering, stated without checking | Re-running the tornado showed sales delay was third |

None of these were caught by reading the code. All were caught by running it against something
independent: a benchmark, a test, a screenshot, or common sense about the numbers.

**What the AI did not do.** It did not do the hand calculation the course requires, and it said so.
It could not test the Claude-generated memo until the team supplied an API key on 5 November; until
then it flagged the gap rather than filling it with invented results. When the memo was finally run
(Claude Sonnet 5.5 and Opus 5.5 through the AIML API gateway), every number in both memos matched the
fact sheet, and the memo itself pointed out a weakness in what it had been given: the fact sheet did
not state what each scenario changed. The memo also noticed, correctly, that the model rewards a
construction delay because it has no delay penalty. Both observations led to changes.

## 3. Validation insights

The four-layer check (Excel recalculated by LibreOffice, three extra cases, an exact-decimal
recomputation, and 383 tests) agreed with the tool to better than 1e−11 on every cash flow figure.
The agreement itself taught us little; the disagreements did.

- The one genuine disagreement between engines (IRR in the heavy-debt case) was not an arithmetic
  error but a property of the finance. Validation found a limitation of the method, not of the code.
- Excel's own IRR() failed on the downside case until given a starting guess. A spreadsheet is not
  automatically more trustworthy than code.
- Testing on 200 random input sets found errors that the base case could never reveal, because the
  base case is well-behaved by construction.
- An AI-generated spreadsheet is a cross-check, not the manual benchmark. The two engines could share
  a misunderstanding (they were written by the same AI from the same assumptions). This is why the
  hand calculation in the validation report still has to be done by a person.

## 4. Practical relevance

A developer or feasibility consultant could use the tool for a first screening of a residential
project, and a lender could use the debt schedule and stress scenarios to size a facility. For real
use the following would have to change:

- Add inflation and price escalation, GST, stamp duty and RERA escrow rules on collections.
- Allow phased launches, multiple unit types and unsold inventory.
- Model interest capitalisation and a moratorium, which most construction finance has.
- Replace the fixed booking-plus-instalment collection pattern with construction-linked plans.
- Add probabilistic analysis for the price and absorption assumptions.
- Audit trail and version control of inputs for each appraisal.

The investment memo was the feature a non-technical reader valued most and the one we trust least.
The template version is safe; the LLM version is only as good as the person who reads it.

## 5. Individual reflections (half a page each, to be written by each member)

- **Maneesha, Project Lead and Finance Modeller.** _Role, what you owned, one thing you now understand about real estate finance that you did not before, one thing you would do differently._
- **Dinesh Sai, Data Lead.** _Where the base case numbers came from, how you judged whether they were realistic, what data you would want for a real project._
- **Sujay, AI and Tool Developer.** _How you worked with the AI, which of its errors you caught, how you decided what to accept._
- **Surya Theja, Validation Engineer.** _The hand calculation, the Goal Seek, what the discrepancies taught you._
- **Akshitha, Documentation and Reflection Lead.** _Keeping the AI log honest, writing for a non-technical reader, what you would change in the manual._

## 6. Ethics and limitations

**Data reliability.** Every input in the base case is an assumption chosen to be round and
plausible, not a market observation. The tool makes those assumptions explicit and auditable, but
it cannot make them true. A real appraisal needs sourced land, cost and price data.

**Over-reliance on AI.** The AI produced working code within minutes, which creates pressure to
trust it. Eight of its errors are listed above; several produced plausible-looking numbers. The
safeguard was not reading the code more carefully but checking outputs against something the AI
did not write. We also note that the AI generated the spreadsheet we validated against, so the
independence of that check is partial.

**Accountability.** A number produced by this tool and quoted in a decision belongs to the person
quoting it, not to the tool or the AI. The memo tab says this explicitly. The number-check guard on
the LLM memo reduces but does not remove the risk of a fabricated figure.

**Confidentiality.** The Claude memo mode sends the fact sheet to an external API. The tool says so
on screen. For a confidential project the template mode, which runs offline, is the only
appropriate choice.

**Disclosure.** All AI use is recorded in the AI usage log with the decision taken on each output.
