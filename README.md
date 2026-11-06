# Real Estate Project Feasibility and Financial Appraisal Tool

CE725 Construction Economics and Finance, IIT Bombay. Course project, Team 8, Topic 2.

Team: Maneesha (Project Lead and Finance Modeller), Dinesh Sai (Data Lead), Sujay (AI and Tool Developer),
Surya Theja (Validation Engineer), Akshitha (Documentation and Reflection Lead).

## What it does

Given land, construction, approval, sales, financing and tax inputs, the tool builds a transparent
monthly cash flow and reports equity NPV, equity and project IRR, payback, profit on cost and the
break-even selling price. It then runs one-at-a-time sensitivity, a tornado chart, preset and custom
stress scenarios, and drafts a plain-language investment memo.

## Run it

```bash
# one-time setup
python3 -m venv .venv            # or: uv venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or: uv pip install -r requirements.txt

# launch
streamlit run app.py
```

Optional: to draft the memo with Claude instead of the offline template, put `AIML_API_KEY` (AIML API
gateway, OpenAI-compatible) or `ANTHROPIC_API_KEY` (Anthropic direct) in `.streamlit/secrets.toml`
(gitignored) or the environment, or paste a key in the Memo tab (it is not stored). The team's AIML key is
configured on the development machine; the memo success path is covered by `tests/ui_test.py`.

## Project layout

```
app.py                       Streamlit user interface
feasibility/
  inputs.py                  ProjectInputs dataclass, base case, validation
  model.py                   monthly cash flow engine (land, approvals, S-curve construction,
                             sales, collections, debt schedule, tax)
  metrics.py                 NPV, IRR, payback, profit on cost, break-even price
  sensitivity.py             one-at-a-time table, tornado, preset scenarios
  memo.py                    template memo, Claude memo, number-check guard
benchmark/
  build_benchmark.py         writes base_case_benchmark.xlsx (pure Excel formulas, no Python values)
  base_case_benchmark.xlsx   the manual-check workbook
  compare.py                 recalculates the workbook (LibreOffice) and prints the discrepancy table
  compare_cases.py           runs three more input cases through copies of the workbook
  hand_check.py              exact-decimal recomputation of the base case from the written assumptions
tests/
  test_model.py              unit tests on NPV, IRR, payback and base-case identities
  test_properties.py         identities on 200 random input sets; agreement with numpy_financial
  test_edge_cases.py         validation, extreme inputs, sensitivity shape, memo number check
  ui_test.py                 browser test of the running app (Playwright + installed Chrome)
docs/
  PROJECT_CHARTER.md         project charter (Annexure B), all ten rows
  USER_MANUAL.md             deliverable 2: user manual
  VALIDATION_REPORT.md       deliverable 3: benchmark vs tool, discrepancies and resolutions
  ai_usage_log.md            deliverable 4: Annexure A log
  REFLECTION_REPORT.md       deliverable 5: learnings and reflection report
  DATA_SOURCES.md            data source list and method note for the base case (19 sources, all opened)
  USER_MANUAL_EXTENDED.md    longer version of the manual with every screen explained
  TEST_REPORT.md             what was tested, how, and what was found
  validation_results.md      raw output of compare.py
  llm_memo_*.md              verbatim Claude memos used to test the number check
  md2pdf.py                  converts the markdown deliverables to PDF (Chrome headless)
  pdf/                       PDF versions of all deliverables
  demo_video.mp4             3-minute demo video of the tool
  screenshots/               browser screenshots from ui_test.py
```

## Base case (benchmark)

| Item | Value |
|---|---|
| Saleable area | 1,00,000 sq ft |
| Selling price | ₹7,500 per sq ft (gross revenue ₹75 cr) |
| Land | ₹20 cr, month 1 |
| Approvals | ₹3 cr, months 1 to 3 |
| Construction | ₹3,000 per sq ft (₹30 cr), months 4 to 30, smoothstep S-curve |
| Sales | months 7 to 30, 20% at booking, balance over 6 months |
| Marketing | 2% of collections |
| Debt | 50% of land, approval and construction spend at 12% p.a., 50% of collections swept to repayment |
| Tax | 25% of project profit, paid in month 36 |
| Discount rate | 15% p.a. effective |

## Validation

```bash
pytest -q                          # 383 tests, about 3 minutes
python benchmark/compare.py        # Python vs Excel, base case (needs LibreOffice or a saved Excel copy)
python benchmark/compare_cases.py  # three more cases through the workbook formulas
python benchmark/hand_check.py     # exact-decimal recomputation of selected months
python tests/ui_test.py            # browser test; run `streamlit run app.py` first; needs Google Chrome
```

The workbook has no values copied from Python; every cell is a formula. The two break-even prices in
the Summary sheet (B21, B22) were obtained by Goal Seek by hand.

The manual benchmark the course requires (months 1, 8 and 36 of the cash flow and the NPV by calculator,
plus Goal Seek) is in section 6 of `docs/VALIDATION_REPORT.md`, re-performed and signed by the Validation
Engineer. A spreadsheet generated with AI help is a cross-check, not a substitute for that step.

## Live app and repository

Live app: https://ce725-real-estate-feasibility.streamlit.app/ (Streamlit Community Cloud; the first load
after idle takes about a minute). Source: https://github.com/dineshsai05/ce725-real-estate-feasibility.
The browser test can be pointed at the deployment with
`APP_URL=https://ce725-real-estate-feasibility.streamlit.app/~/+/ python tests/ui_test.py`; all 27 checks
passed against it on 5 November 2026. Add
`AIML_API_KEY` or `ANTHROPIC_API_KEY` under the app's Secrets if the Claude memo is wanted online.
Never commit `.streamlit/secrets.toml`.

To rebuild the PDFs after editing any document: `python docs/md2pdf.py`.

Data sources and method note for the base case: `docs/DATA_SOURCES.md`.
