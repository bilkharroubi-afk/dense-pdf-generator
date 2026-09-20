# dense-pdf-generator

A small, dependency-light Python tool that turns structured JSON into a clean, print-ready A4 PDF — built for documents where the input length is unpredictable: administrative letters, formal submissions, reports assembled from several source paragraphs.

## The problem

Most "quick PDF from Python" examples fall apart the moment content gets uneven. A short heading followed by a few lines of text looks fine — until a page break lands *between* the heading and its text, and the heading is left stranded alone at the bottom of a page.

I ran into this repeatedly while generating a series of formal documents on tight deadlines, where every one had a different number of sections and paragraph lengths. The fix isn't complicated once you know where to look, but it isn't the first thing you'd think of either.

## The fix

Two small, deliberate choices:

1. **`KeepTogether` around heading + first paragraph.** ReportLab's `platypus` layout engine paginates flowables independently by default — a heading and the paragraph after it are two separate objects that can land on two different pages. Wrapping the pair in `KeepTogether([heading, first_paragraph])` tells the engine to treat them as one atomic block. Later paragraphs in the same section are left outside the block, so a genuinely long section can still flow across a page break — only the heading is protected.

2. **Tighter-than-default margins for dense content.** ReportLab's defaults are tuned for letter-style, sparsely-filled pages. For documents where every line matters (0.9 cm top/bottom, 1.7 cm left/right on A4), the defaults waste real space. These numbers came from trial and error against real print output, not a guess.

Neither fix is exotic — but both are easy to miss until you've watched the same visual bug happen a dozen times.

## Usage

```bash
pip install -r requirements.txt
python generate_pdf.py example_data.json output.pdf
```

Input format:

```json
{
  "title": "Document title",
  "meta": ["Reference: ...", "Date: ..."],
  "sections": [
    {"heading": "1. Section title", "body": "Paragraph one.\n\nParagraph two."}
  ]
}
```

Each `body` can hold multiple paragraphs separated by a blank line (`\n\n`); only the first is pinned to its heading, so long sections still paginate naturally.

## Why this is here

I'm not a developer by trade — B2B SaaS sales background — but I use AI tooling daily to ship small, real utilities rather than just talk about "using AI." This one started as a one-off script to generate formal documents under deadline pressure, got refined over repeated real use, and is generic enough now to be worth sharing rather than sitting in a private folder.

## License

MIT — see [LICENSE](LICENSE).
