"""Extract text from supported estimate documents."""

from pathlib import Path
from typing import Protocol

from app.pdf_text import PdfExtractionError, extract_pdf_text


class DocumentTranscriber(Protocol):
    def transcribe_pdf(self, pdf_path: Path) -> str: ...
    def transcribe_image(self, image_path: Path) -> str: ...


SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".heif"}


def extract_document_text(
    path: Path,
    transcriber: DocumentTranscriber | None = None,
) -> str:
    """Extract local PDF text or use vision OCR for image-based documents."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(path, transcriber)
    if suffix in SUPPORTED_IMAGE_SUFFIXES:
        if transcriber is None:
            raise PdfExtractionError(
                "Image estimates require AI OCR. Configure OPENAI_API_KEY and try again."
            )
        try:
            text = transcriber.transcribe_image(path).strip()
        except Exception as exc:
            raise PdfExtractionError("The image estimate could not be read by AI OCR.") from exc
        if not text:
            raise PdfExtractionError("AI OCR did not find readable text in the image.")
        return text + "\n"
    raise PdfExtractionError(f"Unsupported document type: {suffix or 'unknown'}")
