from pathlib import Path
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

ARTIFACTS = {
    "resume.html": "resume.pdf",
    "cover-letter.html": "cover-letter.pdf",
    "interview-brief.html": "interview-thesis-brief.pdf",
    "120-day-plan.html": "120-day-entry-plan.pdf",
    "executive-fit.html": "executive-fit-brief.pdf",
    "manufacturing-shape-review.html": "manufacturing-shape-review.pdf",
}

for source, output in ARTIFACTS.items():
    HTML(filename=str(ROOT / source), base_url=str(ROOT)).write_pdf(str(DOCS / output))
    print(f"wrote {output}")
