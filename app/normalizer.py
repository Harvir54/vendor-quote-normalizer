"""Convert contractor estimate PDFs into a consistent data structure."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from app.pdf_text import (
    extract_pdf_text,
    find_estimate_total,
    find_money_values,
    find_vendor_name,
)
from app.scope import ScopeItem
from app.trades import get_trade_profile

if TYPE_CHECKING:
    from app.ai_extractor import AIExtractor


NormalizedEstimate = dict[str, Any]


def normalize_estimate_text(
    text: str,
    ai_extractor: "AIExtractor | None" = None,
    trade: str = "painting",
) -> NormalizedEstimate:
    """Extract the currently supported structured fields from quote text."""
    profile = get_trade_profile(trade)
    estimate = cast(NormalizedEstimate, {
        "vendor_name": find_vendor_name(text),
        "estimate_total": find_estimate_total(text),
        "all_money_values": find_money_values(text),
        **{
            field: classifier(text)
            for field, classifier in profile.classifiers.items()
        },
    })

    for field in profile.scope_labels:
        item = estimate[field]
        item["source"] = "rule"
        item["confidence"] = _rule_confidence(item)
        item["review_required"] = item["confidence"] < 0.80

    if ai_extractor is not None:
        from app.ai_extractor import AIExtractionUnavailable, apply_ai_review

        try:
            return apply_ai_review(
                text,
                estimate,
                ai_extractor,
                profile.ai_review_categories,
            )
        except AIExtractionUnavailable:
            return estimate
    return estimate


def _rule_confidence(item: ScopeItem) -> float:
    """Score confidence in a rule's classification, not the contractor's work."""
    status = item["status"]
    has_evidence = item["evidence"] is not None

    if status in ("included", "excluded"):
        return 0.95 if has_evidence else 0.80
    if status == "partial":
        return 0.90
    if status == "unclear":
        return 0.55
    return 0.90 if has_evidence else 0.70


def normalize_estimate(
    pdf_path: Path,
    ai_extractor: "AIExtractor | None" = None,
    trade: str = "painting",
) -> NormalizedEstimate:
    """Extract PDF text and return its normalized estimate fields."""
    return normalize_estimate_text(extract_pdf_text(pdf_path), ai_extractor, trade)
