"""Extract text from digital PDF estimates."""

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
