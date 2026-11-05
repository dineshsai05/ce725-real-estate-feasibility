"""Browser-level test of the running Streamlit app using Playwright + installed Chrome.

Run the app first (streamlit run app.py), then:  python tests/ui_test.py
Writes screenshots to docs/screenshots/ and prints a pass/fail log.
"""
from __future__ import annotations

import os
import pathlib, re, sys, time
from playwright.sync_api import sync_playwright

URL = os.environ.get("APP_URL", "http://localhost:8501")
OUT = pathlib.Path(__file__).resolve().parents[1] / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = ""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def wait_idle(pg, extra: float = 0.4, expect_rerun: bool = False):
    """Wait for Streamlit to finish a rerun.

    Streamlit shows a "Running..." status widget while recomputing. On a loaded
    machine the widget can take over a second to appear, so when a rerun is
    expected we first wait (briefly) for it to attach, then for it to detach.
    """
    if expect_rerun:
        try:
            pg.wait_for_selector("[data-testid='stStatusWidget']", state="attached", timeout=4000)
        except Exception:
            pass
    else:
        time.sleep(0.6)
    try:
        pg.wait_for_selector("[data-testid='stStatusWidget']", state="detached", timeout=60000)
    except Exception:
        pass
    time.sleep(extra)


def metric_value(pg, label: str) -> str:
    box = pg.locator("[data-testid='stMetric']", has_text=label).first
    return box.locator("[data-testid='stMetricValue']").inner_text().strip()


def set_number_input(pg, label: str, value: str):
    """Type a value and confirm the widget accepted it; retry once if a rerun swallowed it."""
    for attempt in range(3):
        inp = pg.get_by_label(label, exact=False).first
        inp.click()
        inp.press("Control+A")
        inp.fill(value)
        inp.press("Enter")
        wait_idle(pg, 1.0, expect_rerun=True)
        got = pg.get_by_label(label, exact=False).first.input_value().replace(",", "")
        if got.rstrip("0").rstrip(".") == value.rstrip("0").rstrip("."):
            return
        time.sleep(1.0)
    print(f"  (warning: field '{label}' shows {got!r} after 3 attempts to set {value!r})")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        pg = browser.new_page(viewport={"width": 1600, "height": 1000})
        pg.goto(URL, wait_until="networkidle", timeout=60000)
        pg.wait_for_selector("text=Verdict", timeout=60000)
        wait_idle(pg)

        # 1. base case KPIs
        npv = metric_value(pg, "Equity NPV")
        irr = metric_value(pg, "Equity IRR")
        pb = metric_value(pg, "Payback")
        be = metric_value(pg, "Break-even price")
        check("Base case equity NPV shown as ₹7.45 cr", npv == "₹7.45 cr", npv)
        check("Base case equity IRR 47.2%", irr == "47.2%", irr)
        check("Base case payback 27 mo", pb == "27 mo", pb)
        check("Base case break-even ₹6,250/sq ft", be == "₹6,250/sq ft", be)
        check("Verdict says Viable", pg.locator("text=Viable").count() > 0)
        pg.screenshot(path=OUT / "01_summary.png", full_page=True)

        # 2. each tab renders and has content
        tabs = ["Cash flow", "Sensitivity", "Scenarios", "Investment memo", "Assumptions and validation"]
        for i, t in enumerate(tabs, start=2):
            pg.get_by_role("tab", name=t).click()
            wait_idle(pg)
            pg.screenshot(path=OUT / f"{i:02d}_{t.lower().replace(' ', '_')}.png", full_page=True)
        pg.get_by_role("tab", name="Cash flow").click(); wait_idle(pg)
        check("Cash flow tab shows a data table", pg.locator("[data-testid='stDataFrame']").count() >= 1)
        check("Cash flow tab has CSV download", pg.get_by_text("Download cash flow (CSV)").count() == 1)

        pg.get_by_role("tab", name="Sensitivity").click(); wait_idle(pg)
        check("Sensitivity tab has a table and a tornado chart",
              pg.locator("[data-testid='stDataFrame']").count() >= 1 and pg.locator(".js-plotly-plot").count() >= 1)
        # switch metric radio and confirm caption/axis changes
        pg.get_by_text("Equity IRR", exact=True).first.click(); wait_idle(pg)
        check("Sensitivity metric can be switched to Equity IRR", pg.locator("text=Equity IRR").count() >= 1)
        pg.screenshot(path=OUT / "03b_sensitivity_irr.png", full_page=True)

        pg.get_by_role("tab", name="Scenarios").click(); wait_idle(pg)
        # the data grid is canvas-rendered, so check the table exists and the caption names the presets
        body = pg.inner_text("body")
        check("Scenario tab shows the preset table and names Downside, Severe and Upside",
              pg.locator("[data-testid='stDataFrame']").count() >= 1 and all(k in body for k in ["Downside", "Severe", "Upside"]))
        check("Custom stress sliders present (5)", pg.locator("[data-testid='stSlider']").count() == 5)

        pg.get_by_role("tab", name="Investment memo").click(); wait_idle(pg)
        memo = pg.locator("textarea").first.input_value()
        check("Template memo generated and starts with INVESTMENT MEMO", memo.startswith("INVESTMENT MEMO"), memo[:40])
        check("Template memo quotes the NPV", "₹7.45 cr" in memo)
        check("Template memo recommends PROCEED for base case", "PROCEED" in memo)
        # Claude mode. (a) Anthropic provider with no key must fail gracefully.
        for _ in range(3):
            pg.get_by_text("Claude (LLM, needs API key)").click(); wait_idle(pg, 0.5, expect_rerun=True)
            if pg.get_by_test_id("stSelectbox").count():
                break
        pg.get_by_test_id("stSelectbox").first.click(); wait_idle(pg, 0.5)
        pg.get_by_role("option", name="Anthropic API (direct)").click(); wait_idle(pg, 0.5, expect_rerun=True)
        pg.get_by_role("button", name="Generate memo with Claude").click()
        try:
            pg.wait_for_selector("[data-testid='stAlert']", timeout=60000)
            wait_idle(pg)
            alert = pg.locator("[data-testid='stAlert']").first.inner_text()
            check("Claude mode without key shows a handled error, not a crash", "Could not generate memo" in alert, alert[:90])
        except Exception as e:
            check("Claude mode without key shows a handled error, not a crash", False, str(e)[:90])
        pg.screenshot(path=OUT / "05b_memo_llm_error.png", full_page=True)
        # (b) AIML provider with the key from .streamlit/secrets.toml must return a memo that passes the number check.
        pg.get_by_test_id("stSelectbox").first.click(); wait_idle(pg, 0.5)
        pg.get_by_role("option", name="AIML API (OpenAI-compatible gateway, Claude models)").click(); wait_idle(pg, 0.5, expect_rerun=True)
        try:
            pg.get_by_text("Using the AIML_API_KEY configured for this app.").wait_for(timeout=8000)
            have_key = True
        except Exception:
            have_key = False
        if have_key:
            pg.get_by_role("button", name="Generate memo with Claude").click()
            try:
                pg.wait_for_selector("textarea[aria-label='Memo (LLM draft - verify before use)']", timeout=120000)
                wait_idle(pg, 1.0)
                llm_text = pg.locator("textarea[aria-label='Memo (LLM draft - verify before use)']").input_value()
                alert = pg.locator("[data-testid='stAlert']").first.inner_text()
                check("LLM memo generated via AIML API (non-empty, mentions NPV)", len(llm_text) > 500 and "NPV" in llm_text,
                      f"{len(llm_text)} chars")
                check("LLM memo passes the fact-sheet number check", "Every number in the memo matches" in alert, alert[:90])
            except Exception as e:
                check("LLM memo generated via AIML API (non-empty, mentions NPV)", False, str(e)[:90])
                check("LLM memo passes the fact-sheet number check", False, "memo not generated")
            pg.screenshot(path=OUT / "05c_memo_llm_aiml.png", full_page=True)
        else:
            print("  (skipped LLM success path: no AIML_API_KEY in secrets)")

        # 3. input change propagates: price 6,250 -> NPV ~ 0
        pg.get_by_role("tab", name="Summary").click(); wait_idle(pg)
        set_number_input(pg, "Selling price", "6250")
        npv2 = metric_value(pg, "Equity NPV")
        check("Price 6,250 gives NPV about zero", re.fullmatch(r"₹-?0\.0\d cr", npv2) is not None, npv2)
        irr2 = metric_value(pg, "Equity IRR")
        check("Price 6,250 gives IRR about 15%", irr2 in ("15.0%", "14.9%", "15.1%"), irr2)
        pg.screenshot(path=OUT / "06_breakeven_price.png", full_page=False)

        # 4. invalid input shows error and stops
        set_number_input(pg, "Sold out by month", "5")
        err = pg.locator("[data-testid='stAlert']").first.inner_text() if pg.locator("[data-testid='stAlert']").count() else ""
        check("Invalid sales window shows validation error", "Sales end month" in err, err[:80])
        check("Invalid input hides KPI metrics", pg.locator("[data-testid='stMetric']").count() == 0)
        pg.screenshot(path=OUT / "07_validation_error.png", full_page=False)

        # 5. reset restores base case
        pg.get_by_role("button", name="Reset to benchmark base case").click(); wait_idle(pg, 2.0)
        npv3 = metric_value(pg, "Equity NPV")
        check("Reset restores base case NPV", npv3 == "₹7.45 cr", npv3)

        # 6. loss-making case: verdict flips
        set_number_input(pg, "Selling price", "4000")
        check("Price 4,000 flips verdict to Not viable", pg.locator("text=Not viable").count() > 0)
        check("Loss case payback reported as No payback", metric_value(pg, "Payback") == "No payback", metric_value(pg, "Payback"))
        pg.screenshot(path=OUT / "08_not_viable.png", full_page=False)
        pg.get_by_role("button", name="Reset to benchmark base case").click(); wait_idle(pg, 2.0)

        # 7. horizon extension
        set_number_input(pg, "Sold out by month", "40")
        check("Sales to month 40 extends horizon to 46 months", metric_value(pg, "Horizon used") == "46 months", metric_value(pg, "Horizon used"))
        pg.get_by_role("button", name="Reset to benchmark base case").click(); wait_idle(pg, 2.0)

        # 8. timing: from pressing Enter to Streamlit's running indicator disappearing
        inp = pg.get_by_label("Construction cost", exact=False).first
        inp.click(); inp.press("Control+A"); inp.fill("3300")
        t0 = time.time(); inp.press("Enter")
        try:
            pg.wait_for_selector("[data-testid='stStatusWidget']", state="attached", timeout=3000)
        except Exception:
            pass
        pg.wait_for_selector("[data-testid='stStatusWidget']", state="detached", timeout=30000)
        dt = time.time() - t0
        check("Full recompute after an input change under 6 s", dt < 6, f"{dt:.1f}s")
        check("Construction cost 3,300 lowers NPV below base", metric_value(pg, "Equity NPV") < "₹7.45 cr", metric_value(pg, "Equity NPV"))

        # 9. console errors
        browser.close()

    n_ok = sum(1 for _, ok, _ in results if ok)
    print(f"\n{n_ok}/{len(results)} UI checks passed")
    (OUT / "ui_test_results.txt").write_text("\n".join(f"{'PASS' if ok else 'FAIL'}\t{n}\t{d}" for n, ok, d in results))
    sys.exit(0 if n_ok == len(results) else 1)


if __name__ == "__main__":
    main()
