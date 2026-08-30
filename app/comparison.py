"""Compare normalized contractor estimates and explain material differences."""

from pathlib import Path
from typing import Any, TypedDict

from app.normalizer import NormalizedEstimate, normalize_estimate


class VendorSummary(TypedDict):
    vendor_name: str | None
    estimate_total: str | None
    total_cents: int | None


class RiskFlag(TypedDict):
    code: str
    severity: str
    vendor_name: str | None
    message: str
    evidence: str | None


class EstimateComparison(TypedDict):
    vendors: list[VendorSummary]
    price_difference_cents: int | None
    lower_bidder: str | None
    scope_comparison: dict[str, dict[str, Any]]
    risk_flags: list[RiskFlag]


SCOPE_LABELS = {
    "walls": "Walls",
    "ceilings": "Ceilings",
    "primer": "Primer",
    "drywall_repair": "Drywall repair",
    "cleanup": "Cleanup",
    "debris_disposal": "Debris disposal",
    "labor_warranty": "Labor warranty",
}


def money_to_cents(value: str | None) -> int | None:
    """Convert a formatted dollar value such as '$4,750.00' into cents."""
    if value is None:
        return None
    cleaned = value.replace("$", "").replace(",", "")
    dollars, decimal = cleaned.split(".")
    return int(dollars) * 100 + int(decimal)


def _scope_matrix(
    first: NormalizedEstimate,
    second: NormalizedEstimate,
) -> dict[str, dict[str, Any]]:
    matrix: dict[str, dict[str, Any]] = {}
    for field, label in SCOPE_LABELS.items():
        matrix[field] = {
            "label": label,
            "first": first[field],
            "second": second[field],
        }
    return matrix


def _risk_flags(
    first: NormalizedEstimate,
    second: NormalizedEstimate,
) -> list[RiskFlag]:
    flags: list[RiskFlag] = []
    estimates = (first, second)

    first_coats = first["walls"]["coat_count"]
    second_coats = second["walls"]["coat_count"]
    if first_coats is not None and second_coats is not None and first_coats != second_coats:
        lower = first if first_coats < second_coats else second
        lower_coats = lower["walls"]["coat_count"]
        higher_coats = max(first_coats, second_coats)
        flags.append(
            {
                "code": "FEWER_WALL_COATS",
                "severity": "high",
                "vendor_name": lower["vendor_name"],
                "message": (
                    f"Includes {lower_coats} wall coat(s), compared with "
                    f"{higher_coats} in the other estimate."
                ),
                "evidence": lower["walls"]["evidence"],
            }
        )

    risk_fields = {
        "ceilings": "ceiling painting",
        "primer": "primer",
        "cleanup": "cleanup",
        "debris_disposal": "debris disposal",
        "labor_warranty": "a labor warranty",
    }
    for field, description in risk_fields.items():
        statuses = [estimate[field]["status"] for estimate in estimates]
        for index, estimate in enumerate(estimates):
            status = statuses[index]
            other_status = statuses[1 - index]
            if other_status != "included" or status == "included":
                continue

            if status == "excluded":
                message = f"Explicitly excludes {description}."
                severity = "high"
            elif status == "not_stated":
                message = f"Does not clearly state whether {description} is included."
                severity = "medium"
            else:
                message = f"Uses unclear or conditional language for {description}."
                severity = "medium"

            flags.append(
                {
                    "code": f"{field.upper()}_{status.upper()}",
                    "severity": severity,
                    "vendor_name": estimate["vendor_name"],
                    "message": message,
                    "evidence": estimate[field]["evidence"],
                }
            )

    return flags


def compare_normalized_estimates(
    first: NormalizedEstimate,
    second: NormalizedEstimate,
) -> EstimateComparison:
    """Return a side-by-side comparison of two normalized estimates."""
    first_cents = money_to_cents(first["estimate_total"])
    second_cents = money_to_cents(second["estimate_total"])

    price_difference_cents = None
    lower_bidder = None
    if first_cents is not None and second_cents is not None:
        price_difference_cents = abs(first_cents - second_cents)
        if first_cents < second_cents:
            lower_bidder = first["vendor_name"]
        elif second_cents < first_cents:
            lower_bidder = second["vendor_name"]

    return {
        "vendors": [
            {
                "vendor_name": first["vendor_name"],
                "estimate_total": first["estimate_total"],
                "total_cents": first_cents,
            },
            {
                "vendor_name": second["vendor_name"],
                "estimate_total": second["estimate_total"],
                "total_cents": second_cents,
            },
        ],
        "price_difference_cents": price_difference_cents,
        "lower_bidder": lower_bidder,
        "scope_comparison": _scope_matrix(first, second),
        "risk_flags": _risk_flags(first, second),
    }


def compare_estimates(first_pdf: Path, second_pdf: Path) -> EstimateComparison:
    """Normalize and compare two contractor estimate PDFs."""
    return compare_normalized_estimates(
        normalize_estimate(first_pdf),
        normalize_estimate(second_pdf),
    )
