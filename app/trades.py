"""Trade-specific extraction and comparison configuration."""

from collections.abc import Callable
from dataclasses import dataclass

from app.scope import (
    ScopeItem,
    classify_ceilings,
    classify_cleanup,
    classify_debris_disposal,
    classify_drywall_repair,
    classify_labor_warranty,
    classify_primer,
    classify_walls,
)
from app.flooring_scope import (
    classify_baseboards,
    classify_existing_floor_removal,
    classify_flooring_installation,
    classify_moisture_barrier,
    classify_subfloor_preparation,
    classify_transitions,
    classify_underlayment,
)


ScopeClassifier = Callable[[str], ScopeItem]


@dataclass(frozen=True)
class TradeProfile:
    """Define the fields and language rules used for one contractor trade."""

    key: str
    label: str
    scope_labels: dict[str, str]
    classifiers: dict[str, ScopeClassifier]
    risk_descriptions: dict[str, str]
    ai_review_categories: tuple[str, ...]


PAINTING = TradeProfile(
    key="painting",
    label="Interior painting",
    scope_labels={
        "walls": "Walls",
        "ceilings": "Ceilings",
        "primer": "Primer",
        "drywall_repair": "Drywall repair",
        "cleanup": "Cleanup",
        "debris_disposal": "Debris disposal",
        "labor_warranty": "Labor warranty",
    },
    classifiers={
        "ceilings": classify_ceilings,
        "walls": classify_walls,
        "primer": classify_primer,
        "drywall_repair": classify_drywall_repair,
        "cleanup": classify_cleanup,
        "debris_disposal": classify_debris_disposal,
        "labor_warranty": classify_labor_warranty,
    },
    risk_descriptions={
        "ceilings": "ceiling painting",
        "primer": "primer",
        "cleanup": "cleanup",
        "debris_disposal": "debris disposal",
        "labor_warranty": "a labor warranty",
    },
    ai_review_categories=(
        "ceilings",
        "walls",
        "primer",
        "drywall_repair",
        "cleanup",
        "debris_disposal",
        "labor_warranty",
    ),
)

FLOORING = TradeProfile(
    key="flooring",
    label="Flooring",
    scope_labels={
        "flooring_installation": "Flooring installation",
        "existing_floor_removal": "Existing floor removal",
        "subfloor_preparation": "Subfloor preparation",
        "underlayment": "Underlayment",
        "moisture_barrier": "Moisture barrier",
        "transitions": "Transitions",
        "baseboards": "Baseboards",
        "cleanup": "Cleanup",
        "labor_warranty": "Labor warranty",
    },
    classifiers={
        "flooring_installation": classify_flooring_installation,
        "existing_floor_removal": classify_existing_floor_removal,
        "subfloor_preparation": classify_subfloor_preparation,
        "underlayment": classify_underlayment,
        "moisture_barrier": classify_moisture_barrier,
        "transitions": classify_transitions,
        "baseboards": classify_baseboards,
        "cleanup": classify_cleanup,
        "labor_warranty": classify_labor_warranty,
    },
    risk_descriptions={
        "existing_floor_removal": "existing floor removal",
        "subfloor_preparation": "subfloor preparation",
        "underlayment": "underlayment",
        "moisture_barrier": "a moisture barrier",
        "transitions": "transition pieces",
        "baseboards": "baseboard work",
        "cleanup": "cleanup",
        "labor_warranty": "a labor warranty",
    },
    ai_review_categories=(
        "flooring_installation",
        "existing_floor_removal",
        "subfloor_preparation",
        "underlayment",
        "moisture_barrier",
        "transitions",
        "baseboards",
        "cleanup",
        "labor_warranty",
    ),
)

TRADE_PROFILES = {profile.key: profile for profile in (PAINTING, FLOORING)}


class UnsupportedTradeError(ValueError):
    """Raised when a requested trade does not have a configured profile."""


def get_trade_profile(trade: str) -> TradeProfile:
    """Return a configured trade profile by its stable key."""
    try:
        return TRADE_PROFILES[trade]
    except KeyError as exc:
        supported = ", ".join(TRADE_PROFILES)
        raise UnsupportedTradeError(
            f"Unsupported trade '{trade}'. Supported trades: {supported}."
        ) from exc


def supported_trades() -> list[dict[str, str]]:
    """Return API-safe metadata for all configured trade profiles."""
    return [
        {"key": profile.key, "label": profile.label}
        for profile in TRADE_PROFILES.values()
    ]
