"""Classify residential HVAC estimate scope and equipment specifications."""

import re
from typing import TypedDict

from app.scope import ScopeItem, _classify_simple_scope, _joined_evidence_options


class HVACSystemItem(ScopeItem):
    system_types: list[str]
    capacity_tons: float | None


class HVACEquipmentItem(ScopeItem):
    manufacturer: str | None
    model_numbers: list[str]


class HVACEfficiencyItem(ScopeItem):
    seer2: float | None
    eer2: float | None
    hspf2: float | None
    afue_percent: float | None


def _first_number(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text, re.IGNORECASE)
    return float(match.group(1).replace(",", "")) if match else None


def classify_hvac_system(text: str) -> HVACSystemItem:
    definitions = (
        ("central air conditioner", r"\b(?:central air conditioner|air conditioning system|AC system|A/C system)\b"),
        ("heat pump", r"\bheat pump\b"),
        ("gas furnace", r"\b(?:gas furnace|furnace)\b"),
        ("ductless mini-split", r"\b(?:ductless|mini[- ]split)\b"),
        ("packaged system", r"\b(?:packaged unit|package unit|rooftop unit)\b"),
        ("air handler", r"\bair handler\b"),
    )
    system_types = [
        label for label, pattern in definitions if re.search(pattern, text, re.IGNORECASE)
    ]
    evidence_options = _joined_evidence_options(
        text, "|".join(f"(?:{pattern})" for _, pattern in definitions)
    )
    capacity = _first_number(text, r"\b(\d+(?:\.\d+)?)\s*(?:-| )?ton(?:s|nage)?\b")
    if capacity is None:
        btu = _first_number(text, r"\b(\d{2,3}(?:,\d{3})?)\s*BTU(?:/?H|H)?\b")
        capacity = round(btu / 12000, 2) if btu else None
    return {
        "status": "included" if system_types else "not_stated",
        "evidence": evidence_options[0] if evidence_options else None,
        "system_types": system_types,
        "capacity_tons": capacity,
    }


def classify_hvac_equipment(text: str) -> HVACEquipmentItem:
    options = _joined_evidence_options(
        text,
        r"\b(?:manufacturer|brand|model|condenser|outdoor unit|indoor unit|coil|air handler|furnace)\b",
    )
    model_numbers = []
    for match in re.finditer(
        r"\b(?:model|model number|model #|outdoor unit|indoor unit|condenser|coil|air handler)\s*[:#-]?\s*([A-Z0-9][A-Z0-9.-]{4,})",
        text,
        re.IGNORECASE,
    ):
        model = match.group(1).rstrip(".,;")
        if (
            any(character.isdigit() for character in model)
            and model not in model_numbers
        ):
            model_numbers.append(model)
    manufacturer_match = re.search(
        r"\b(?:manufacturer|brand)\s*[:#-]?\s*([A-Za-z][A-Za-z ]{1,24})(?=\s*(?:\n|,|;|\.|model))",
        text,
        re.IGNORECASE,
    )
    return {
        "status": "included" if options else "not_stated",
        "evidence": options[0] if options else None,
        "manufacturer": manufacturer_match.group(1).strip() if manufacturer_match else None,
        "model_numbers": model_numbers,
    }


def classify_hvac_efficiency(text: str) -> HVACEfficiencyItem:
    options = _joined_evidence_options(text, r"\b(?:SEER2?|EER2?|HSPF2?|AFUE)\b")
    evidence = " ".join(options)
    return {
        "status": "included" if options else "not_stated",
        "evidence": evidence or None,
        "seer2": _first_number(text, r"\b(\d+(?:\.\d+)?)\s*SEER2\b"),
        "eer2": _first_number(text, r"\b(\d+(?:\.\d+)?)\s*EER2\b"),
        "hspf2": _first_number(text, r"\b(\d+(?:\.\d+)?)\s*HSPF2\b"),
        "afue_percent": _first_number(text, r"\b(\d+(?:\.\d+)?)\s*%?\s*AFUE\b"),
    }


def classify_load_calculation(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:Manual J|load calculation|heat load calculation|system sizing)\b",
        ("manual j", "calculation", "perform", "included", "includes"),
    )


def classify_matched_system(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:AHRI|matched system|matched equipment|certified match)\b",
        ("ahri", "matched", "certificate", "reference", "included"),
    )


def classify_ductwork(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:ductwork|duct work|ducts?|return air|supply register)\b",
        ("install", "replace", "repair", "seal", "modify", "modification", "reuse", "reused", "included", "includes"),
    )


def classify_thermostat(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:thermostat|temperature control)\b",
        ("install", "replace", "included", "includes", "provide", "thermostat"),
    )


def classify_electrical(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:electrical|disconnect|breaker|circuit|line voltage)\b",
        ("install", "replace", "included", "includes", "provide", "connect"),
    )


def classify_refrigerant_lines(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:refrigerant lines?|line set|lineset)\b",
        ("install", "replace", "flush", "reuse", "included", "includes"),
    )


def classify_condensate(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:condensate|drain pan|float switch)\b",
        ("install", "replace", "included", "includes", "provide"),
    )


def classify_permit(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text, r"\b(?:permit|inspection fees?)\b",
        ("permit", "obtain", "included", "includes"),
    )


def classify_commissioning(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:commissioning|startup|start-up|airflow test|static pressure|refrigerant charge|system testing)\b",
        ("commission", "startup", "start-up", "test", "verify", "included"),
    )


def classify_removal_disposal(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:remove|removal|haul|dispose|disposal)\b.*\b(?:existing|old)?\s*(?:HVAC|equipment|unit|condenser|furnace|coil)\b|"
        r"\b(?:existing|old)\s+(?:HVAC\s+)?(?:equipment|unit|condenser|furnace|coil)\b.*\b(?:remove|removal|haul|dispose|disposal)\b",
        ("remove", "removal", "haul", "dispose", "disposal", "included"),
    )
