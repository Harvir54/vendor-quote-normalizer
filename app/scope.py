"""Classify normalized scope items using evidence from estimate text."""

import re
from typing import Literal, TypedDict


ScopeStatus = Literal["included", "excluded", "not_stated", "unclear"]


class ScopeItem(TypedDict):
    status: ScopeStatus
    evidence: str | None


def _sentences_containing(text: str, keyword: str) -> list[str]:
    """Return cleaned sentences or lines containing a keyword."""
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [
        chunk.strip()
        for chunk in chunks
        if keyword.lower() in chunk.lower() and chunk.strip()
    ]


def classify_ceilings(text: str) -> ScopeItem:
    """Classify whether ceiling painting is included in an estimate."""
    evidence_options = _sentences_containing(text, "ceiling")

    if not evidence_options:
        return {"status": "not_stated", "evidence": None}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            phrase in lowered
            for phrase in ("not included", "excluded", "excluding")
        ):
            return {"status": "excluded", "evidence": evidence}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            phrase in lowered
            for phrase in ("not specified", "not stated", "not addressed")
        ):
            return {"status": "not_stated", "evidence": evidence}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            phrase in lowered
            for phrase in ("may", "optional", "if requested", "to be determined")
        ):
            return {"status": "unclear", "evidence": evidence}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            word in lowered
            for word in ("paint", "apply", "coat", "included", "includes")
        ):
            return {"status": "included", "evidence": evidence}

    return {"status": "unclear", "evidence": evidence_options[0]}
