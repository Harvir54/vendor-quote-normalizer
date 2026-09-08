"""Classify plumbing-estimate scope and fixture quantities."""

import re
from typing import TypedDict

from app.scope import ScopeItem, _classify_simple_scope, _joined_evidence_options


class FixtureInstallationItem(ScopeItem):
    fixture_count: int | None
    fixture_types: list[str]


class PlumbingProjectItem(ScopeItem):
    project_types: list[str]


class WaterHeaterItem(ScopeItem):
    tankless: bool | None
    capacity_gallons: int | None
    fuel_type: str | None


def classify_plumbing_project(text: str) -> PlumbingProjectItem:
    """Identify one or more explicitly stated plumbing job types."""
    lowered = text.lower()
    definitions = (
        ("fixture replacement", r"\b(?:install|replace|set)\b.*\b(?:fixture|toilet|faucet|sink|shower|tub)s?\b"),
        ("water heater", r"\b(?:water heater|tankless)\b"),
        ("repipe", r"\b(?:repipe|re-pipe|whole[- ]house piping)\b"),
        ("sewer or drain replacement", r"\b(?:sewer|drain)\s+(?:line\s+)?(?:replacement|repair)\b"),
        ("leak repair", r"\b(?:leak repair|repair\s+(?:a\s+)?leak|pipe leak)\b"),
        ("drain cleaning", r"\b(?:drain cleaning|hydro[- ]?jet|snaking|cable cleaning)\b"),
    )
    project_types = [
        label for label, pattern in definitions if re.search(pattern, lowered, re.IGNORECASE)
    ]
    evidence_options = _joined_evidence_options(
        text,
        "|".join(f"(?:{pattern})" for _, pattern in definitions),
    )
    return {
        "status": "included" if project_types else "not_stated",
        "evidence": evidence_options[0] if evidence_options else None,
        "project_types": project_types,
    }


def classify_fixture_installation(text: str) -> FixtureInstallationItem:
    evidence_options = _joined_evidence_options(
        text,
        r"\b(?:install|replace|set)\b.*\b(?:toilets?|faucets?|sinks?|fixtures?|showers?|tubs?)\b",
    )
    if not evidence_options:
        return {"status": "not_stated", "evidence": None, "fixture_count": None, "fixture_types": []}
    evidence = evidence_options[0]
    lowered = evidence.lower()
    status = "excluded" if "not included" in lowered or "excluded" in lowered else "included"
    count_match = re.search(r"\b(\d+)\s+(?:customer-supplied\s+)?(?:plumbing\s+)?fixtures?\b", evidence, re.IGNORECASE)
    fixture_types = [name for name in ("toilet", "faucet", "sink", "shower", "tub") if name in lowered]
    return {
        "status": status,
        "evidence": evidence,
        "fixture_count": int(count_match.group(1)) if count_match else None,
        "fixture_types": fixture_types,
    }


def classify_supply_lines(text: str) -> ScopeItem:
    return _classify_simple_scope(text, r"\bsupply lines?\b|\bwater lines?\b", ("install", "replace", "included", "includes"))


def classify_drain_lines(text: str) -> ScopeItem:
    return _classify_simple_scope(text, r"\bdrain lines?\b|\bwaste lines?\b", ("install", "replace", "included", "includes"))


def classify_shutoff_valves(text: str) -> ScopeItem:
    return _classify_simple_scope(text, r"\bshut-?off valves?\b|\bstop valves?\b", ("install", "replace", "included", "includes"))


def classify_permit(text: str) -> ScopeItem:
    return _classify_simple_scope(text, r"\bpermits?\b|\binspection fees?\b", ("permit", "included", "includes", "obtain"))


def classify_materials(text: str) -> ScopeItem:
    return _classify_simple_scope(text, r"\bmaterials?\b|\bparts?\b", ("materials", "parts", "included", "includes"))


def classify_testing(text: str) -> ScopeItem:
    return _classify_simple_scope(text, r"\bpressure test(?:ing)?\b|\bleak test(?:ing)?\b|\btest for leaks\b", ("test", "testing", "included", "includes"))


def classify_water_heater(text: str) -> WaterHeaterItem:
    options = _joined_evidence_options(text, r"\b(?:water heater|tankless)\b")
    if not options:
        return {
            "status": "not_stated",
            "evidence": None,
            "tankless": None,
            "capacity_gallons": None,
            "fuel_type": None,
        }
    evidence = " ".join(options)
    lowered = evidence.lower()
    capacity = re.search(r"\b(\d{2,3})[- ]gallon\b", evidence, re.IGNORECASE)
    fuel_type = next((
        fuel for fuel in ("natural gas", "propane", "electric", "heat pump")
        if fuel in lowered
    ), None)
    return {
        "status": "excluded" if any(
            term in lowered for term in ("not included", "excluded")
        ) else "included",
        "evidence": evidence,
        "tankless": "tankless" in lowered,
        "capacity_gallons": int(capacity.group(1)) if capacity else None,
        "fuel_type": fuel_type,
    }


def classify_removal_disposal(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:remove|removal|haul|dispose|disposal)\b.*"
        r"\b(?:fixture|toilet|faucet|sink|water heater|pipe|piping|equipment)\b|"
        r"\b(?:existing|old)\s+(?:fixture|toilet|water heater|pipe|piping|equipment)\b",
        ("remove", "removal", "haul", "dispose", "disposal", "included"),
    )


def classify_access_restoration(text: str) -> ScopeItem:
    item = _classify_simple_scope(
        text,
        r"\b(?:drywall|wall|floor|concrete|stucco|cabinet)\b.*"
        r"\b(?:patch(?:ing)?|repair|restore|restoration|access|cutting)\b|"
        r"\b(?:patch(?:ing)?|repair|restore|restoration)\b.*"
        r"\b(?:drywall|wall|floor|concrete|stucco|cabinet)\b",
        ("patch", "repair", "restore", "restoration", "included", "includes"),
    )
    evidence = item["evidence"]
    if evidence and re.search(
        r"\b(?:owner|customer|tenant)\b.*\b(?:responsible|to provide|by)\b|"
        r"\b(?:by|responsibility of)\s+(?:the\s+)?(?:owner|customer|tenant)\b",
        evidence,
        re.IGNORECASE,
    ):
        item["status"] = "excluded"
    return item


def classify_camera_inspection(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:sewer camera|camera inspection|video inspection)\b",
        ("camera", "inspection", "included", "includes", "perform"),
    )


def classify_excavation(text: str) -> ScopeItem:
    return _classify_simple_scope(
        text,
        r"\b(?:excavat(?:e|ion|ing)|trench(?:ing)?|backfill)\b",
        ("excavate", "excavation", "trench", "trenching", "backfill", "included"),
    )
