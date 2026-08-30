"""Classify normalized scope items using evidence from estimate text."""

import re
from typing import Literal, TypedDict


ScopeStatus = Literal["included", "excluded", "not_stated", "unclear"]


class ScopeItem(TypedDict):
    status: ScopeStatus
    evidence: str | None


class WallScopeItem(ScopeItem):
    coat_count: int | None


class RepairScopeItem(ScopeItem):
    limitations: list[str]


class WarrantyScopeItem(ScopeItem):
    duration_years: int | None


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
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


def _joined_evidence_options(text: str, pattern: str) -> list[str]:
    """Find matching chunks and reconnect nearby lines split by PDF layout."""
    chunks = _sentence_chunks(text)
    options: list[str] = []

    for index, chunk in enumerate(chunks):
        if not re.search(pattern, chunk, re.IGNORECASE):
            continue

        evidence = chunk
        if index > 0:
            previous = chunks[index - 1]
            is_wrapped_prose = (
                not re.search(r"[.!?;:]$", previous)
                and re.search(r"[A-Za-z]", previous)
                and not previous.isupper()
            )
            if is_wrapped_prose:
                evidence = f"{previous} {evidence}"
        next_index = index + 1
        while next_index < len(chunks) and next_index <= index + 3:
            needs_continuation = not re.search(r"[.!?;:]$", evidence)
            abbreviation_split = bool(
                re.search(r"\b(?:sq|ft)\.$", evidence, re.IGNORECASE)
            )
            if not needs_continuation and not abbreviation_split:
                break
            evidence = f"{evidence} {chunks[next_index]}"
            next_index += 1
        options.append(evidence)

    return options


def _classify_simple_scope(
    text: str,
    pattern: str,
    included_terms: tuple[str, ...],
) -> ScopeItem:
    """Classify a straightforward scope category from matching evidence."""
    evidence_options = _joined_evidence_options(text, pattern)
    if not evidence_options:
        return {"status": "not_stated", "evidence": None}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(term in lowered for term in ("not included", "excluded", "excluding")):
            return {"status": "excluded", "evidence": evidence}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(term in lowered for term in ("not specified", "not stated", "not addressed")):
            return {"status": "not_stated", "evidence": evidence}

    conditional_terms = (
        "may",
        "optional",
        "if needed",
        "as needed",
        "if requested",
        "to be determined",
    )
    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(term in lowered for term in conditional_terms):
            return {"status": "unclear", "evidence": evidence}

    for evidence in evidence_options:
        lowered = evidence.lower()
        if any(term in lowered for term in included_terms):
            return {"status": "included", "evidence": evidence}

    return {"status": "unclear", "evidence": evidence_options[0]}


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


def classify_drywall_repair(text: str) -> RepairScopeItem:
    """Classify minor drywall preparation and retain stated limitations."""
    evidence_options = _joined_evidence_options(
        text,
        r"\bdrywall\b|\bnail holes?\b|\bminor dents?\b",
    )
    if not evidence_options:
        return {"status": "not_stated", "evidence": None, "limitations": []}

    limitation_terms = (
        "not included",
        "excluded",
        "larger than",
        "beyond",
        "quoted separately",
    )
    limitations = [
        evidence
        for evidence in evidence_options
        if any(term in evidence.lower() for term in limitation_terms)
    ]

    for evidence in evidence_options:
        lowered = evidence.lower()
        is_limitation = any(term in lowered for term in limitation_terms)
        includes_repair = any(
            term in lowered
            for term in ("patch", "fill", "filling", "repair", "minor dents")
        )
        if includes_repair and not is_limitation:
            return {
                "status": "included",
                "evidence": evidence,
                "limitations": limitations,
            }

    for evidence in evidence_options:
        lowered = evidence.lower()
        if "not specified" in lowered or "not stated" in lowered:
            return {
                "status": "not_stated",
                "evidence": evidence,
                "limitations": limitations,
            }

    if limitations:
        has_full_exclusion = any(
            "not included" in item.lower() or "excluded" in item.lower()
            for item in limitations
        )
        return {
            "status": "excluded" if has_full_exclusion else "unclear",
            "evidence": limitations[0],
            "limitations": limitations,
        }

    return {
        "status": "unclear",
        "evidence": evidence_options[0],
        "limitations": [],
    }


def classify_cleanup(text: str) -> ScopeItem:
    """Classify jobsite cleanup."""
    return _classify_simple_scope(
        text,
        r"\bcleanup\b|\bcleaning\b",
        ("includes", "included", "cleanup", "cleaning"),
    )


def classify_debris_disposal(text: str) -> ScopeItem:
    """Classify debris or waste disposal."""
    return _classify_simple_scope(
        text,
        r"\bdisposal\b|\bdispose\b|\bhauling\b|\bdebris removal\b",
        ("legal disposal", "disposal included", "dispose", "hauling", "debris removal"),
    )


def classify_labor_warranty(text: str) -> WarrantyScopeItem:
    """Classify the labor warranty and extract its duration in years."""
    result = _classify_simple_scope(
        text,
        r"\bwarrant(?:y|ies)\b",
        ("labor warranty", "workmanship warranty", "warranty included"),
    )
    evidence = result["evidence"]
    if evidence:
        evidence = re.sub(r"^WARRANTY\s+", "", evidence, flags=re.IGNORECASE)

    duration_years = None
    if evidence:
        match = re.search(
            r"\b(one|two|three|four|five|\d+)[ -]year\b",
            evidence,
            re.IGNORECASE,
        )
        if match:
            value = match.group(1).lower()
            duration_years = NUMBER_WORDS.get(
                value, int(value) if value.isdigit() else None
            )

    return {
        "status": result["status"],
        "evidence": evidence,
        "duration_years": duration_years,
    }
