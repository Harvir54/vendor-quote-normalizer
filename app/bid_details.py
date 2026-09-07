"""Extract shared contract details without inferring missing promises."""

import re
from typing import TypedDict


class BidDetails(TypedDict):
    proposal_number: str | None
    issued_date: str | None
    valid_until: str | None
    contractor_license: str | None
    project_schedule: str | None
    payment_terms: str | None
    exclusions: str | None


def _first_group(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = " ".join(match.group(1).split()).strip(" .|")
            return re.sub(
                r"^(?:TERMS(?: AND ACCEPTANCE)?)\s+",
                "",
                value,
                flags=re.IGNORECASE,
            )
    return None


def extract_bid_details(text: str) -> BidDetails:
    """Return common bid fields only when supported by document text."""
    flowing_text = " ".join(text.split())
    return {
        "proposal_number": _first_group(text, (
            r"(?:estimate|proposal|quote)\s*#\s*:?\s*([A-Z0-9-]+)",
            r"(?:estimate|proposal|quote)\s+([A-Z]{1,5}-\d{2,})\b",
        )),
        "issued_date": _first_group(text, (
            r"^(?:issued|date)\s*:?\s*([A-Z]+\s+\d{1,2},\s+\d{4})\s*$",
            r"^(?:issued|date)\s*:?\s*(\d{1,2}/\d{1,2}/\d{2,4})\s*$",
        )),
        "valid_until": _first_group(text, (
            r"^valid[ \t]+through[ \t]*:?[ \t]*([^\n]+)$",
            r"^(pricing\s+(?:is\s+)?held\s+for\s+[^\n.]+)",
            r"^.*?\b(valid\s+for\s+\d+\s+days)\b.*$",
        )),
        "contractor_license": _first_group(text, (
            r"\b(?:CA\s+)?Lic(?:ense)?\.?\s*#\s*([A-Z0-9-]+)",
        )),
        "project_schedule": _first_group(flowing_text, (
            r"(?:^|[.!?])\s*([^.!?]*\b(?:expected|estimated|scheduled|planned)\b"
            r"[^.!?]*\b(?:working\s+days?|business\s+days?|weeks?)\b[^.!?]*)",
            r"(?:^|[.!?])\s*([^.!?]*\bwork\s+can\s+begin\b[^.!?]*)",
        )),
        "payment_terms": _first_group(flowing_text, (
            r"(?:^|[.!?])\s*([^.!?]*\b\d{1,3}%\s+"
            r"(?:deposit|at\s+scheduling)\b[^.!?]*)",
            r"(?:^|[.!?])\s*([^.!?]*\bpayment\s+schedule\s*:[^.!?]*)",
        )),
        "exclusions": _first_group(text, (
            r"(?:^EXCLUSIONS\s*$|^NOT INCLUDED\s*$)\s*"
            r"([\s\S]+?)(?=^(?:TERMS|ALLOWANCES|WARRANTY|SCOPE|PROJECT)\b|\Z)",
        )),
    }
