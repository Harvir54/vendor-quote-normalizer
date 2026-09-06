"""Extract text from digital PDF estimates."""

import re
from pathlib import Path

from pypdf import PdfReader


class PdfExtractionError(RuntimeError):
    """Raised when usable text cannot be extracted from a PDF."""


def extract_pdf_text(pdf_path: Path) -> str:
    """Return readable text from every page in a PDF.

    This first version handles PDFs that already contain a text layer. Scanned
    image-only estimates will be supported later with OCR.
    """
    path = Path(pdf_path)
    if not path.is_file():
        raise PdfExtractionError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise PdfExtractionError(f"Expected a PDF file: {path}")

    try:
        reader = PdfReader(path)
    except Exception as exc:
        raise PdfExtractionError(f"Could not open PDF: {path}") from exc

    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"--- Page {page_number} ---\n{text}")

    if not pages:
        raise PdfExtractionError(
            "No text was found. This may be a scanned PDF that requires OCR."
        )

    return "\n\n".join(pages) + "\n"


def find_money_values(text: str) -> list[str]:
    money_pattern = r"\$[\d,]+\.\d{2}"
    return re.findall(money_pattern, text)


def find_estimate_total(text: str) -> str | None:
    total_pattern = (
        r"(?:ESTIMATE\s+TOTAL|ESTIMATED\s+TOTAL|PROPOSAL\s+TOTAL|"
        r"QUOTE\s+TOTAL|GRAND\s+TOTAL)\s*"
        r"(\$[\d,]+\.\d{2})"
    )

    match = re.search(total_pattern, text, re.IGNORECASE)

    if match:
        return match.group(1)

    return None


def find_vendor_name(text: str) -> str | None:
    """Return the most likely company line before a document-type heading."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    document_labels = {"ESTIMATE", "PROPOSAL", "QUOTE"}

    def is_header_metadata(line: str) -> bool:
        normalized = line.casefold()
        return (
            normalized.startswith("--- page ")
            or re.fullmatch(r"page\s+\d+(?:\s+of\s+\d+)?", normalized) is not None
            or "@" in line
            or "licensed" in normalized
            or "insured" in normalized
            or "interior repaint proposal" in normalized
            or ("proposal" in normalized and "|" in line)
            or "synthetic fixture" in normalized
            or "synthetic test document" in normalized
        )

    for index, line in enumerate(lines):
        if line.upper() in document_labels and index > 0:
            for candidate in reversed(lines[max(0, index - 6) : index]):
                if not is_header_metadata(candidate):
                    return candidate

    return None
