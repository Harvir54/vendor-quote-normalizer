"""Convert contractor estimate PDFs into a consistent data structure."""

from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from app.pdf_text import (
    extract_pdf_text,
    find_estimate_total,
    find_money_values,
    find_vendor_name,
)
from app.scope import (
    RepairScopeItem,
    ScopeItem,
    WallScopeItem,
    WarrantyScopeItem,
    classify_ceilings,
    classify_cleanup,
    classify_debris_disposal,
    classify_drywall_repair,
    classify_labor_warranty,
    classify_primer,
    classify_walls,
)

if TYPE_CHECKING:
    from app.ai_extractor import AIExtractor


class NormalizedEstimate(TypedDict):
    vendor_name: str | None
    estimate_total: str | None
    all_money_values: list[str]
    ceilings: ScopeItem
    walls: WallScopeItem
    primer: ScopeItem
    drywall_repair: RepairScopeItem
    cleanup: ScopeItem
    debris_disposal: ScopeItem
    labor_warranty: WarrantyScopeItem


def normalize_estimate_text(
    text: str,
    ai_extractor: "AIExtractor | None" = None,
) -> NormalizedEstimate:
    """Extract the currently supported structured fields from quote text."""
    estimate: NormalizedEstimate = {
        "vendor_name": find_vendor_name(text),
        "estimate_total": find_estimate_total(text),
        "all_money_values": find_money_values(text),
        "ceilings": classify_ceilings(text),
        "walls": classify_walls(text),
        "primer": classify_primer(text),
        "drywall_repair": classify_drywall_repair(text),
        "cleanup": classify_cleanup(text),
        "debris_disposal": classify_debris_disposal(text),
        "labor_warranty": classify_labor_warranty(text),
    }

    for field in (
        "ceilings",
        "walls",
        "primer",
        "drywall_repair",
        "cleanup",
        "debris_disposal",
        "labor_warranty",
    ):
        item = estimate[field]
        item["source"] = "rule"
        item["confidence"] = _rule_confidence(item)
        item["review_required"] = item["confidence"] < 0.80

    if ai_extractor is not None:
        from app.ai_extractor import AIExtractionUnavailable, apply_ai_review

        try:
            return apply_ai_review(text, estimate, ai_extractor)
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
) -> NormalizedEstimate:
    """Extract PDF text and return its normalized estimate fields."""
    return normalize_estimate_text(extract_pdf_text(pdf_path), ai_extractor)
