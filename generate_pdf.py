"""
dense-pdf-generator
--------------------
Turns structured JSON (sections of text, some short, some long) into a clean,
print-ready A4 PDF — built for documents where you can't control the input
length: administrative letters, legal submissions, formal correspondence,
reports assembled from several source documents.

Why this exists
----------------
Most "quick PDF from Python" tutorials break down the moment your content is
uneven: a short heading followed by three lines of text looks fine until a
page break lands *between* the heading and its text, orphaning the heading
at the bottom of a page. The two fixes below are the actual reason this
script exists — they came out of generating dozens of real administrative
documents on tight deadlines and noticing the same visual bug every time.

1. Every (heading + first paragraph) pair is wrapped in a ReportLab
   `KeepTogether` flowable, so the layout engine treats them as one atomic
   block for pagination purposes. A heading can never render as the last
   line on a page with its content pushed to the next one.

2. Margins are tuned tight (0.9cm top/bottom, 1.7cm left/right) for dense
   single-spaced content, rather than ReportLab's default letter-style
   margins, which waste ~15% of the page on documents where every line
   counts.

Usage
-----
    python generate_pdf.py example_data.json output.pdf

Input format (see example_data.json):
    {
      "title": "Document title",
      "meta": ["Reference: ...", "Date: ..."],   # optional small header lines
      "sections": [
        {"heading": "1. Section title", "body": "One or more paragraphs..."},
        ...
      ]
    }
"""

import json
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    KeepTogether,
)

MARGIN_TOP_BOTTOM = 0.9 * cm
MARGIN_LEFT_RIGHT = 1.7 * cm


def build_styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "DocTitle",
        parent=base["Title"],
        fontSize=14,
        leading=17,
        spaceAfter=10,
    )
    meta = ParagraphStyle(
        "Meta",
        parent=base["Normal"],
        fontSize=9,
        leading=12,
        textColor="#444444",
        spaceAfter=2,
    )
    heading = ParagraphStyle(
        "SectionHeading",
        parent=base["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontSize=10,
        leading=13.5,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    return title, meta, heading, body


def build_pdf(data: dict, output_path: str) -> None:
    title_style, meta_style, heading_style, body_style = build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=MARGIN_TOP_BOTTOM,
        bottomMargin=MARGIN_TOP_BOTTOM,
        leftMargin=MARGIN_LEFT_RIGHT,
        rightMargin=MARGIN_LEFT_RIGHT,
        title=data.get("title", "Document"),
    )

    story = []

    if data.get("title"):
        story.append(Paragraph(data["title"], title_style))

    for line in data.get("meta", []):
        story.append(Paragraph(line, meta_style))

    if data.get("meta"):
        story.append(Spacer(1, 8))

    for section in data.get("sections", []):
        heading_para = Paragraph(section["heading"], heading_style)
        body_paragraphs = [
            Paragraph(p, body_style)
            for p in section["body"].split("\n\n")
            if p.strip()
        ]
        # Heading + its first paragraph are kept on the same page.
        # Remaining paragraphs (for long sections) can still flow naturally.
        block = [heading_para] + body_paragraphs[:1]
        story.append(KeepTogether(block))
        story.extend(body_paragraphs[1:])

    doc.build(story)


def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_pdf.py <input.json> <output.pdf>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    build_pdf(data, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
