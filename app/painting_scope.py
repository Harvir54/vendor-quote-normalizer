"""Classify painting preparation, protection, and coating specifications."""

import re
from typing import TypedDict

from app.scope import ScopeItem, _classify_simple_scope, _joined_evidence_options


class PaintSpecificationItem(ScopeItem):
    manufacturer: str | None
    product_line: str | None
    sheens: list[str]


def classify_surface_preparation(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:surface preparation|surface prep|prep and paint|sanding|"
        r"scraping|deglossing|caulking|nail holes?)\b",
        ("prepare", "preparation", "prep", "sand", "scrape", "fill", "caulk"),
    )


def classify_property_protection(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:protect|protection|drop cloths?|masking|cover)\b.*"
        r"\b(?:floor|counter|appliance|fixture|furnishing|surface)\b|"
        r"\b(?:floor|counter|appliance|fixture|furnishing|surface)s?\b.*"
        r"\b(?:protect|protection|drop cloths?|masking|cover)\b",
        ("protect", "protection", "drop cloth", "masking", "cover"),
    )


def classify_trim_and_doors(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:baseboards?|trim|door casings?|door frames?|interior doors?)\b",
        ("paint", "apply", "coat", "renew", "included", "includes"),
    )


def classify_paint_specifications(text: str) -> PaintSpecificationItem:
    options = _joined_evidence_options(
        text,
        r"\b(?:Sherwin-Williams|Benjamin Moore|Behr|PPG|Dunn-Edwards|"
        r"eggshell|flat|matte|satin|semi-gloss|gloss|acrylic|enamel|"
        r"contractor-grade|premium paint)\b",
    )
    if not options:
        return {
            "status": "not_stated",
            "evidence": None,
            "manufacturer": None,
            "product_line": None,
            "sheens": [],
        }

    evidence = " ".join(options)
    combined = " ".join(options)
    lowered = combined.lower()
    manufacturer = next((
        label
        for label in ("Sherwin-Williams", "Benjamin Moore", "Behr", "PPG", "Dunn-Edwards")
        if label.lower() in lowered
    ), None)
    product_line = None
    for label in ("Duration Home", "Emerald", "SuperPaint", "Aura", "Regal Select"):
        if label.lower() in lowered:
            product_line = label
            break
    sheens = [
        label
        for label in ("flat", "matte", "eggshell", "satin", "semi-gloss", "gloss")
        if re.search(rf"\b{re.escape(label)}\b", lowered)
    ]
    status = "excluded" if any(
        phrase in lowered for phrase in ("not included", "excluded")
    ) else "included"
    return {
        "status": status,
        "evidence": evidence,
        "manufacturer": manufacturer,
        "product_line": product_line,
        "sheens": sheens,
    }


def classify_lead_safety(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:lead-safe|lead based paint|lead-based paint|lead(?: or asbestos)? testing|"
        r"lead abatement|hazardous coatings?)\b",
        ("lead-safe", "testing", "abatement", "included", "includes"),
    )
