"""Classify flooring-specific scope and retain material specifications."""

import re
from typing import NotRequired, TypedDict

from app.scope import ScopeItem, _classify_simple_scope, _joined_evidence_options


class FlooringInstallationItem(ScopeItem):
    area_sq_ft: int | None
    material_type: str | None
    wear_layer_mil: int | None
    thickness_mm: float | None


class UnderlaymentItem(ScopeItem):
    attached: NotRequired[bool | None]


def _number(text: str, pattern: str, *, decimal: bool = False) -> int | float | None:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).replace(",", "")
    return float(value) if decimal else int(value)


def _material_type(text: str) -> str | None:
    lowered = text.lower()
    materials = (
        ("luxury vinyl plank", ("luxury vinyl plank", "lvp")),
        ("engineered hardwood", ("engineered hardwood",)),
        ("laminate", ("laminate",)),
        ("carpet", ("carpet",)),
        ("tile", ("tile",)),
    )
    for label, terms in materials:
        if any(term in lowered for term in terms):
            return label
    return None


def classify_flooring_installation(text: str) -> FlooringInstallationItem:
    """Classify installation and extract area and product specifications."""
    evidence_options = _joined_evidence_options(
        text,
        r"\binstall(?:ation|ing)?\b.*\b(?:floor|lvp|vinyl|laminate|hardwood|carpet|tile)\b|"
        r"\b(?:floor|lvp|vinyl|laminate|hardwood|carpet|tile)\b.*\binstall(?:ation|ing)?\b",
    )
    if not evidence_options:
        return {
            "status": "not_stated",
            "evidence": None,
            "area_sq_ft": None,
            "material_type": None,
            "wear_layer_mil": None,
            "thickness_mm": None,
        }

    evidence = evidence_options[0]
    lowered = evidence.lower()
    status = "included"
    if any(term in lowered for term in ("not included", "excluded", "excluding")):
        status = "excluded"
    elif any(term in lowered for term in ("if needed", "optional", "to be determined")):
        status = "unclear"

    return {
        "status": status,
        "evidence": evidence,
        "area_sq_ft": _number(
            evidence,
            r"\b([\d,]+)\s*(?:sq\.?\s*ft\.?|square feet|sf)\b",
        ),
        "material_type": _material_type(evidence),
        "wear_layer_mil": _number(evidence, r"\b(\d+)\s*mil\b"),
        "thickness_mm": _number(
            evidence,
            r"\b(\d+(?:\.\d+)?)\s*mm\b",
            decimal=True,
        ),
    }


def classify_existing_floor_removal(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:remove|removal|demo(?:lition)?)\b.*\b(?:floor|carpet|tile|vinyl|laminate)\b|"
        r"\bexisting (?:floor|flooring|carpet|tile|vinyl|laminate)\b",
        ("remove", "removal", "demolition", "included", "includes"),
    )


def classify_subfloor_preparation(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\bsubfloor\b|\bfloor (?:prep|preparation|leveling|levelling)\b",
        ("prepare", "preparation", "prep", "leveling", "levelling", "included"),
    )


def classify_underlayment(text: str) -> UnderlaymentItem:
    result = _classify_simple_scope(
        text,
        r"\bunderlayment\b|\battached pad\b",
        ("underlayment", "attached pad", "included", "includes"),
    )
    evidence = result["evidence"]
    return {
        **result,
        "attached": bool(evidence and "attached" in evidence.lower()),
    }


def classify_moisture_barrier(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\bmoisture barrier\b|\bvapor barrier\b",
        ("moisture barrier", "vapor barrier", "included", "includes"),
    )


def classify_transitions(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\btransitions?\b|\btransition strips?\b|\breducers?\b",
        ("transition", "reducer", "included", "includes", "install"),
    )


def classify_baseboards(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\bbaseboards?\b|\bbase moulding\b|\bbase molding\b",
        ("baseboard", "base moulding", "base molding", "included", "install"),
    )
