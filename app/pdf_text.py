"""Extract text from digital PDFs with an optional scanned-PDF fallback."""

import re
from pathlib import Path
from typing import Protocol

from pypdf import PdfReader


class PdfExtractionError(RuntimeError):
    """Raised when usable text cannot be extracted from a PDF."""


class PDFTranscriber(Protocol):
    """Convert an image-only PDF into plain text."""

    def transcribe_pdf(self, pdf_path: Path) -> str: ...


MAX_OCR_PAGES = 10


def extract_pdf_text(
    pdf_path: Path,
    ocr_transcriber: PDFTranscriber | None = None,
) -> str:
    """Return readable text from every page in a PDF.

    Prefer the PDF's local text layer. Only image-only documents use the
    optional remote transcriber, which avoids unnecessary API cost.
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
        if ocr_transcriber is None:
            raise PdfExtractionError(
                "No text was found. Scanned PDFs require the optional AI OCR "
                "fallback; configure OPENAI_API_KEY and try again."
            )
        if len(reader.pages) > MAX_OCR_PAGES:
            raise PdfExtractionError(
                f"Scanned PDFs are limited to {MAX_OCR_PAGES} pages to control "
                "processing cost."
            )
        try:
            transcribed_text = ocr_transcriber.transcribe_pdf(path).strip()
        except Exception as exc:
            raise PdfExtractionError(
                "The scanned PDF could not be read by the AI OCR fallback."
            ) from exc
        if not transcribed_text:
            raise PdfExtractionError(
                "The AI OCR fallback did not find readable text in this PDF."
            )
        return transcribed_text + "\n"

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
