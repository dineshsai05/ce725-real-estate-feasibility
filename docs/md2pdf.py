"""Convert the markdown deliverables in docs/ to PDF.

Markdown -> HTML (python-markdown, tables + fenced code) -> PDF (Google Chrome headless).
Chrome is used because it prints Unicode (₹, −, ≥, ☐) and HTML tables correctly without a LaTeX install.

Usage: python docs/md2pdf.py [file.md ...]      (default: all deliverables)
Output: docs/pdf/<name>.pdf and a page count per file.
"""
from __future__ import annotations

import pathlib, shutil, subprocess, sys

import markdown

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "pdf"
DEFAULT = ["USER_MANUAL.md", "VALIDATION_REPORT.md", "ai_usage_log.md", "REFLECTION_REPORT_DRAFT.md",
           "DATA_SOURCES.md", "TEST_REPORT.md", "PRESENTATION_AND_DEMO.md"]

CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
body { font-family: "Liberation Serif", "DejaVu Serif", Georgia, serif; font-size: 10.5pt; line-height: 1.32;
       color: #111; max-width: none; }
h1 { font-size: 17pt; margin: 0 0 4pt 0; }
h2 { font-size: 12.5pt; margin: 11pt 0 3pt 0; border-bottom: 1px solid #999; padding-bottom: 1pt; }
h3 { font-size: 11pt; margin: 8pt 0 2pt 0; }
p { margin: 3pt 0 5pt 0; }
ul, ol { margin: 2pt 0 5pt 0; padding-left: 18pt; }
li { margin: 1pt 0; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 7pt 0; font-size: 9pt; line-height: 1.22;
        page-break-inside: auto; }
th, td { border: 1px solid #aaa; padding: 2pt 4pt; vertical-align: top; text-align: left; }
th { background: #eee; }
tr { page-break-inside: avoid; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.8pt; background: #f3f3f3; padding: 0 2px; }
pre { background: #f3f3f3; border: 1px solid #ddd; padding: 5pt; font-size: 8.5pt; white-space: pre-wrap; }
hr { border: 0; border-top: 1px solid #bbb; margin: 8pt 0; }
"""


def to_pdf(md_path: pathlib.Path) -> tuple[pathlib.Path, int]:
    html_body = markdown.markdown(md_path.read_text(encoding="utf-8"),
                                  extensions=["tables", "fenced_code", "sane_lists"])
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    OUT.mkdir(exist_ok=True)
    html_path = OUT / (md_path.stem + ".html")
    html_path.write_text(html, encoding="utf-8")
    pdf_path = OUT / (md_path.stem + ".pdf")
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                   check=True, capture_output=True, timeout=120)
    html_path.unlink()
    info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
    pages = int(next(l.split()[-1] for l in info.splitlines() if l.startswith("Pages:")))
    return pdf_path, pages


def main(argv: list[str]) -> None:
    files = [pathlib.Path(a) for a in argv] or [HERE / f for f in DEFAULT]
    for f in files:
        pdf, pages = to_pdf(f)
        print(f"{pdf.name:32s} {pages:3d} pages")


if __name__ == "__main__":
    main(sys.argv[1:])
