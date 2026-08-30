"""Classify normalized scope items using evidence from estimate text."""

import re
from typing import Literal, TypedDict


ScopeStatus = Literal["included", "excluded", "not_stated", "unclear"]


class ScopeItem(TypedDict):
    status: ScopeStatus
    evidence: str | None


class WallScopeItem(ScopeItem):
    coat_count: int | None


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
}


def _sentence_chunks(text: str) -> list[str]:
    """Split extracted text into non-empty, cleaned sentences or lines."""
    return [
        chunk.strip()
        for chunk in re.split(r"(?<=[.!?])\s+|\n+", text)
        if chunk.strip()
    ]


def _sentences_containing(text: str, keyword: str) -> list[str]:
    """Return cleaned sentences or lines containing a keyword."""
    return [
        chunk
        for chunk in _sentence_chunks(text)
        if keyword.lower() in chunk.lower()
    ]


def _find_coat_count(text: str) -> int | None:
    """Return a numeric coat count from wording such as 'two finish coats'."""
    match = re.search(
        r"\b(one|two|three|four|\d+)\s+(?:finish\s+)?coats?\b",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None

    value = match.group(1).lower()
    return NUMBER_WORDS.get(value, int(value) if value.isdigit() else None)


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


def classify_walls(text: str) -> WallScopeItem:
    """Classify wall painting and extract the stated number of coats."""
    chunks = _sentence_chunks(text)
    wall_indexes = [
        index
        for index, chunk in enumerate(chunks)
        if re.search(r"\bwalls?\b", chunk, re.IGNORECASE)
    ]

    if not wall_indexes:
        return {"status": "not_stated", "evidence": None, "coat_count": None}

    evidence_options: list[str] = []
    for index in wall_indexes:
        evidence = chunks[index]
        if _find_coat_count(evidence) is None and index + 1 < len(chunks):
            next_chunk = chunks[index + 1]
            if "coat" in next_chunk.lower():
                evidence = f"{evidence} {next_chunk}"
                if not re.search(r"[.!?]$", next_chunk) and index + 2 < len(chunks):
                    evidence = f"{evidence} {chunks[index + 2]}"
        evidence_options.append(evidence)

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            phrase in lowered
            for phrase in ("not included", "excluded", "excluding")
        ):
            return {"status": "excluded", "evidence": evidence, "coat_count": None}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            phrase in lowered
            for phrase in ("not specified", "not stated", "not addressed")
        ):
            return {
                "status": "not_stated",
                "evidence": evidence,
                "coat_count": None,
            }

    for evidence in evidence_options:
        lowered = evidence.lower()
        is_conditional = any(
            phrase in lowered
            for phrase in ("may", "optional", "if requested", "to be determined")
        )
        describes_work = any(
            word in lowered
            for word in ("paint", "apply", "coat", "included", "includes")
        )
        if describes_work and not is_conditional:
            return {
                "status": "included",
                "evidence": evidence,
                "coat_count": _find_coat_count(evidence),
            }

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            phrase in lowered
            for phrase in ("may", "optional", "if requested", "to be determined")
        ):
            return {
                "status": "unclear",
                "evidence": evidence,
                "coat_count": _find_coat_count(evidence),
            }

    return {
        "status": "unclear",
        "evidence": evidence_options[0],
        "coat_count": _find_coat_count(evidence_options[0]),
    }


def classify_primer(text: str) -> ScopeItem:
    """Classify whether primer or spot-priming is included."""
    evidence_options = [
        chunk
        for chunk in _sentence_chunks(text)
        if re.search(r"\bprim(?:e|er|ing)\b", chunk, re.IGNORECASE)
    ]

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
            for phrase in (
                "may",
                "optional",
                "if needed",
                "as needed",
                "if requested",
                "to be determined",
            )
        ):
            return {"status": "unclear", "evidence": evidence}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(
            phrase in lowered
            for phrase in ("prime", "primer", "priming", "included", "includes")
        ):
            return {"status": "included", "evidence": evidence}

    return {"status": "unclear", "evidence": evidence_options[0]}
