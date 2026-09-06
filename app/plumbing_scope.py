"""Classify plumbing-estimate scope and fixture quantities."""

import re
from typing import TypedDict

from app.scope import ScopeItem, _classify_simple_scope, _joined_evidence_options


class FixtureInstallationItem(ScopeItem):
    fixture_count: int | None
    fixture_types: list[str]


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
