"""Convert contractor estimate PDFs into a consistent data structure."""

from pathlib import Path
from typing import TypedDict

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


def normalize_estimate_text(text: str) -> NormalizedEstimate:
    """Extract the currently supported structured fields from quote text."""
    return {
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


def normalize_estimate(pdf_path: Path) -> NormalizedEstimate:
    """Extract PDF text and return its normalized estimate fields."""
    return normalize_estimate_text(extract_pdf_text(pdf_path))
