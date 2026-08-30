"""Command-line interface for the extraction prototype."""

import argparse
import sys
from pathlib import Path

from app.pdf_text import PdfExtractionError, extract_pdf_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract readable text from a contractor estimate PDF."
    )
    parser.add_argument("pdf", type=Path, help="Path to the estimate PDF")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional text output file; prints to the terminal when omitted",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        text = extract_pdf_text(args.pdf)
    except PdfExtractionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Extracted text saved to {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
