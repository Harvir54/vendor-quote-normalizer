"""Interpret low-confidence estimate scope using structured model output."""

import os
from contextlib import suppress
from pathlib import Path
from typing import Any, Literal, Protocol, cast

from pydantic import BaseModel, Field

from app.normalizer import NormalizedEstimate


ReviewCategory = Literal[
    "ceilings",
    "walls",
    "primer",
    "drywall_repair",
    "surface_preparation",
    "property_protection",
    "trim_and_doors",
    "paint_specifications",
    "lead_safety",
    "cleanup",
    "debris_disposal",
    "labor_warranty",
    "flooring_installation",
    "existing_floor_removal",
    "subfloor_preparation",
    "underlayment",
    "moisture_barrier",
    "moisture_testing",
    "waste_allowance",
    "acclimation",
    "furniture_appliances",
    "transitions",
    "baseboards",
    "fixture_installation",
    "supply_lines",
    "drain_lines",
    "shutoff_valves",
    "permit",
    "materials",
    "testing",
]
ReviewStatus = Literal["included", "partial", "excluded", "not_stated", "unclear"]


class AIClassification(BaseModel):
    category: ReviewCategory
    status: ReviewStatus
    evidence: str | None
    confidence: float = Field(ge=0, le=1)


class AIExtractionBatch(BaseModel):
    classifications: list[AIClassification]


class StructuredResponse(Protocol):
    output_parsed: AIExtractionBatch | None


class AIExtractor(Protocol):
    def classify(
        self,
        estimate_text: str,
        categories: list[ReviewCategory],
    ) -> AIExtractionBatch: ...


class AIExtractionUnavailable(RuntimeError):
    """Raised when the optional model service cannot complete a review."""


class OpenAIExtractor:
    """Use the Responses API to classify only rule-flagged scope categories."""

    def __init__(self, client: Any | None = None, model: str | None = None):
        if client is None:
            # Keep the large optional SDK off the startup path when AI is disabled.
            from openai import OpenAI

            client = OpenAI()
        self.client = client
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6")

    def classify(
        self,
        estimate_text: str,
        categories: list[ReviewCategory],
    ) -> AIExtractionBatch:
        try:
            response: StructuredResponse = self.client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Classify contractor-estimate scope using only the supplied "
                            "document. Return one result per requested category. Evidence "
                            "must be an exact contiguous quote from the document. If the "
                            "document does not support a decision, use not_stated with null "
                            "evidence. Do not infer promises that are not written."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Requested categories: {', '.join(categories)}\n\n"
                            f"Estimate text:\n{estimate_text}"
                        ),
                    },
                ],
                text_format=AIExtractionBatch,
            )
        except Exception as exc:
            raise AIExtractionUnavailable(
                "AI review is temporarily unavailable; rule results were preserved."
            ) from exc
        if response.output_parsed is None:
            raise ValueError("The model did not return a structured extraction.")
        return response.output_parsed

    def transcribe_pdf(self, pdf_path: Path) -> str:
        """Transcribe an image-only estimate using PDF page vision."""
        uploaded_file = None
        try:
            with pdf_path.open("rb") as pdf:
                uploaded_file = self.client.files.create(
                    file=pdf,
                    purpose="user_data",
                )
            response = self.client.responses.create(
                model=os.getenv("OPENAI_OCR_MODEL", self.model),
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": uploaded_file.id,
                            },
                            {
                                "type": "input_text",
                                "text": (
                                    "Transcribe all visible text in this contractor "
                                    "estimate. Preserve reading order, line breaks, "
                                    "prices, quantities, headings, exclusions, and "
                                    "warranty terms. Do not summarize, correct, infer, "
                                    "or add any text. Return only the transcription."
                                ),
                            },
                        ],
                    }
                ],
            )
            return response.output_text
        except Exception as exc:
            raise AIExtractionUnavailable(
                "AI OCR is temporarily unavailable."
            ) from exc
        finally:
            if uploaded_file is not None:
                with suppress(Exception):
                    self.client.files.delete(uploaded_file.id)


def configured_ai_extractor() -> OpenAIExtractor | None:
    """Return an extractor only when the backend process has an API key."""
    if not os.getenv("OPENAI_API_KEY"):
        return None
    return OpenAIExtractor()


def apply_ai_review(
    text: str,
    estimate: NormalizedEstimate,
    extractor: AIExtractor,
    review_categories: tuple[str, ...] = (
        "ceilings",
        "walls",
        "primer",
        "drywall_repair",
        "cleanup",
        "debris_disposal",
        "labor_warranty",
    ),
) -> NormalizedEstimate:
    """Replace flagged rule results only after validating model evidence."""
    categories = [
        cast(ReviewCategory, field)
        for field in review_categories
        if estimate[field]["review_required"]
    ]
    if not categories:
        return estimate

    batch = extractor.classify(text, categories)
    seen: set[str] = set()
    for result in batch.classifications:
        if result.category not in categories or result.category in seen:
            continue
        seen.add(result.category)

        evidence_is_valid = result.evidence is None or result.evidence in text
        absence_is_valid = result.status == "not_stated" and result.evidence is None
        if not evidence_is_valid or (result.evidence is None and not absence_is_valid):
            continue

        item = estimate[result.category]
        item["status"] = result.status
        item["evidence"] = result.evidence
        item["source"] = "ai"
        item["confidence"] = result.confidence
        item["review_required"] = result.confidence < 0.80

    return estimate
