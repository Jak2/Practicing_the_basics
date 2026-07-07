#!/usr/bin/env python3
"""
Convert a PDF to a Markdown file using pymupdf (fitz).
Usage: python pdf_to_md.py <input.pdf> [output.md]
If output path is omitted, writes <input_stem>.md alongside the PDF.
"""

import sys
from pathlib import Path


def pdf_to_markdown(pdf_path: Path, out_path: Path) -> None:
    try:
        import fitz  # pymupdf
    except ImportError:
        print("pymupdf not installed. Run: pip install pymupdf")
        sys.exit(1)

    doc = fitz.open(pdf_path)
    lines = []

    for page in doc:
        blocks = page.get_text("blocks")
        # blocks: (x0, y0, x1, y1, text, block_no, block_type)
        blocks_sorted = sorted(blocks, key=lambda b: (round(b[1] / 10), b[0]))
        for block in blocks_sorted:
            text = block[4].strip()
            if text:
                lines.append(text)
        lines.append("")  # blank line between pages

    doc.close()
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    pdf = Path(sys.argv[1]).resolve()
    if not pdf.exists():
        print(f"File not found: {pdf}")
        sys.exit(1)

    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else pdf.with_suffix(".md")
    pdf_to_markdown(pdf, out)
