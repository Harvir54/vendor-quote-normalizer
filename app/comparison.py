"""Compare normalized contractor estimates and explain material differences."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

from app.normalizer import NormalizedEstimate, normalize_estimate
from app.trades import TradeProfile, get_trade_profile

if TYPE_CHECKING:
    from app.ai_extractor import AIExtractor


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
    profile: TradeProfile,
) -> dict[str, dict[str, Any]]:
    matrix: dict[str, dict[str, Any]] = {}
    for field, label in profile.scope_labels.items():
        matrix[field] = {
            "label": label,
            "first": first[field],
            "second": second[field],
        }
    return matrix


def _risk_flags(
    first: NormalizedEstimate,
    second: NormalizedEstimate,
    profile: TradeProfile,
) -> list[RiskFlag]:
    flags: list[RiskFlag] = []
    estimates = (first, second)

    first_coats = first["walls"]["coat_count"] if profile.key == "painting" else None
    second_coats = second["walls"]["coat_count"] if profile.key == "painting" else None
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

    if profile.key == "flooring":
        first_install = first["flooring_installation"]
        second_install = second["flooring_installation"]
        first_area = first_install["area_sq_ft"]
        second_area = second_install["area_sq_ft"]
        if first_area and second_area and first_area != second_area:
            lower = first if first_area < second_area else second
            lower_area = min(first_area, second_area)
            higher_area = max(first_area, second_area)
            flags.append({
                "code": "FLOOR_AREA_MISMATCH",
                "severity": "high",
                "vendor_name": lower["vendor_name"],
                "message": (
                    f"Prices {lower_area:,} sq ft, compared with {higher_area:,} sq ft "
                    "in the other estimate. Confirm both bids cover the same area."
                ),
                "evidence": lower_install["evidence"] if (
                    lower_install := lower["flooring_installation"]
                ) else None,
            })

        first_wear = first_install["wear_layer_mil"]
        second_wear = second_install["wear_layer_mil"]
        if first_wear and second_wear and first_wear != second_wear:
            lower = first if first_wear < second_wear else second
            flags.append({
                "code": "LOWER_WEAR_LAYER",
                "severity": "high",
                "vendor_name": lower["vendor_name"],
                "message": (
                    f"Specifies a {min(first_wear, second_wear)} mil wear layer, compared "
                    f"with {max(first_wear, second_wear)} mil in the other estimate."
                ),
                "evidence": lower["flooring_installation"]["evidence"],
            })

    if profile.key == "plumbing":
        first_count = first["fixture_installation"]["fixture_count"]
        second_count = second["fixture_installation"]["fixture_count"]
        if first_count and second_count and first_count != second_count:
            lower = first if first_count < second_count else second
            flags.append({
                "code": "FIXTURE_COUNT_MISMATCH",
                "severity": "high",
                "vendor_name": lower["vendor_name"],
                "message": (
                    f"Prices {min(first_count, second_count)} fixtures, compared with "
                    f"{max(first_count, second_count)} in the other estimate."
                ),
                "evidence": lower["fixture_installation"]["evidence"],
            })

    for field, description in profile.risk_descriptions.items():
        statuses = [estimate[field]["status"] for estimate in estimates]
        for index, estimate in enumerate(estimates):
            status = statuses[index]
            other_status = statuses[1 - index]
            if other_status != "included" or status == "included":
                continue

            if status == "excluded":
                message = f"Explicitly excludes {description}."
                severity = "high"
            elif status == "partial":
                message = f"Includes only part of the requested {description} scope."
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
    trade: str = "painting",
) -> EstimateComparison:
    """Return a side-by-side comparison of two normalized estimates."""
    profile = get_trade_profile(trade)
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
        "scope_comparison": _scope_matrix(first, second, profile),
        "risk_flags": _risk_flags(first, second, profile),
    }


def compare_estimates(
    first_pdf: Path,
    second_pdf: Path,
    ai_extractor: "AIExtractor | None" = None,
    trade: str = "painting",
) -> EstimateComparison:
    """Normalize and compare two contractor estimate PDFs."""
    return compare_normalized_estimates(
        normalize_estimate(first_pdf, ai_extractor, trade),
        normalize_estimate(second_pdf, ai_extractor, trade),
        trade,
    )
