# Learnings and Reflection Report (DRAFT for the team to edit)

Real Estate Project Feasibility and Financial Appraisal Tool. CE725 Course Project, Team 8, Topic 2.
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

**What the AI did not do.** It did not do the hand calculation the course requires on its own authority:
it produced a calculator-style first pass on 5 November, labelled it as not satisfying the requirement, and
the Validation Engineer re-performed every line by hand before it was accepted.
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
  hand calculation in the validation report was re-performed by a person, and why that re-performance
  found the same figures only because the two engines and the calculator all follow the written conventions
  in the manual.

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

## 5. Individual reflections (half a page each)

> **Draft status.** These five reflections were drafted by the AI assistant on 5 November 2026 from the
> project record (the AI usage log, the validation report, the data source list and the test report) and
> are written in the first person as a starting point only. Each member must rewrite their reflection in
> their own words, add or remove anything that does not match their experience, and sign it. Text in
> [square brackets] is a prompt for the member to fill in. Submitting these unedited would be presenting
> AI output as personal reflection, which the course treats as misconduct. The AI's role in drafting them
> is recorded in AI usage log entry 33.

**Maneesha, Project Lead and Finance Modeller.** [Draft, to be rewritten by Maneesha.]
My role was to own the economic logic: the choice of a monthly discounted cash flow at the equity level,
the conventions in section 7 of the manual, and the base case. The thing I understand now that I did not
at the start is that IRR is not a property of a project but of a cash flow pattern. When we ran a
heavy-debt case, the tool said −14% and Excel said 839%, and both were right, because a large bullet
repayment makes the equity cash flow change sign twice. Until then I had treated IRR as the number a
developer quotes; now I would quote NPV at a stated hurdle rate and treat IRR as a cross-check. The second
learning was how much leverage flatters equity IRR: 47% equity IRR against 34% project IRR is the loan
working, not the project, and a lender would only look at the second figure. What I would do differently is
decide the discount rate from evidence before building rather than after: the EY/NSE survey puts the real
estate cost of equity at 16.4% and we built on 15%, which is defensible but was a guess at the time.
[Add: how you divided the work and timeline, and one decision you made that the AI disagreed with.]

**Dinesh Sai, Data Lead.** [Draft, to be rewritten by Dinesh.]
My job was to find out whether the base case numbers were real. The honest answer is that for the first
week they were not: they were round, plausible figures the AI proposed and we accepted, and no document said
where they came from. Fixing that meant choosing a market, the peripheral Mumbai Metropolitan Region, and
checking all 21 inputs against published sources. The most useful thing I learned is the difference between
an asking price, a ready reckoner rate and a registered transaction rate: for Kalyan these were ₹9,750,
₹6,039 and ₹7,900 per sq ft on the same day, and our ₹7,500 only looks right against the last of them.
The second thing was that search summaries lie by omission. The first repo rate the AI reported was 5.25%;
the RBI had raised it to 5.50% a month earlier, and only opening the RBI release caught it. I opened the
MDPI paper myself when the AI's tools were blocked and found that the mean IRR hurdle it had quoted was not
on the page; only the median was. For a real project I would want the actual MCGM premium schedule for the
plot, a construction-linked payment plan from a comparable launch, and a lender term sheet, because the
three inputs we had to label optimistic (instalments, marketing, approvals) are exactly the ones that a
published average cannot settle.

**Sujay, AI and Tool Developer.** [Draft, to be rewritten by Sujay.]
I was responsible for the build and for deciding what to accept from the AI. The pattern that worked was
never accepting code on the strength of it running. Every function was accepted only when something
independent agreed with it: the Excel workbook, the numpy_financial library, a property test over 200
random input sets, or a screenshot. That caught the errors that mattered: the IRR function returned nothing
for the base case because its bracket was wrong; the loan was almost unused because it funded construction
only; the sensitivity table had fifteen columns; and one input change took 28 seconds because the
sensitivity loop was solving two break-even prices it did not need. None of these would have been found by
reading the code, and all of them were found by testing it. [Add: the Streamlit Cloud deployment, what went
wrong with the iframe, and the one AI suggestion you rejected outright.] What I now believe about AI-assisted
coding is that the AI is fast at producing a plausible version and poor at knowing when it is wrong; the
developer's job moves from writing the code to designing the checks that would expose it.

**Surya Theja, Validation Engineer.** [Draft, to be rewritten by Surya.]
My role was the manual benchmark, and the course is right to insist on it. The Excel workbook and the
Python engine agreed to fourteen decimal places, which sounds like proof until you remember both were
written by the same AI from the same assumptions; agreement between them only proves they share a reading.
Redoing months 1, 8 and 36 with a calculator was the first time a person had followed the written
conventions independently. Month 8 was the instructive one: getting the S-curve share, the instalment on
the previous month's booking, the interest on the opening balance and the repayment cap in the right order
takes about twenty minutes, and the only differences from the tool were in the fourth decimal, from my own
rounding. The NPV sum of 36 present values came to 7.4514 against the tool's 7.4515 for the same reason.
Goal Seek reproduced both break-even prices. What the discrepancies in section 7 of the validation report
taught me is that most of them were not arithmetic: they were the AI's test being wrong about finance (NPV
does not always fall when the rate rises) or Excel's own IRR failing without a starting guess. [Add: how
long the full hand check took and what you would check next with more time.]

**Akshitha, Documentation and Reflection Lead.** [Draft, to be rewritten by Akshitha.]
I owned the AI usage log, the user manual and this report. The hardest part of the log was keeping the
Decision column honest. It is easy to write Accept under every entry; the entries worth reading are the
Modify and Reject ones, and the ones where the AI's output was wrong and we say so: the stale repo rate, the
mean hurdle rate that was not in the paper, the tornado colours that were inverted, the test assumptions that
were false. A log with no rejections would tell an evaluator we had not been checking. For the manual, the
discipline was length. The first version was eight pages and read as a tour of the screen; the submitted
four pages keep only what a user needs to act: inputs, how to read each metric, the conventions, where the
numbers came from and what is not modelled. Writing for a director who will never open the tool also
shaped the memo: the number check that flags any figure not in the fact sheet exists because a reader of the
memo cannot verify it themselves. [Add: what you would change in the manual after watching someone use the
tool for the first time, and how the log was maintained during the build rather than reconstructed.]

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
