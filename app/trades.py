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
    classify_acclimation,
    classify_baseboards,
    classify_existing_floor_removal,
    classify_flooring_installation,
    classify_furniture_appliances,
    classify_moisture_barrier,
    classify_moisture_testing,
    classify_subfloor_preparation,
    classify_transitions,
    classify_underlayment,
    classify_waste_allowance,
)
from app.painting_scope import (
    classify_lead_safety,
    classify_paint_specifications,
    classify_property_protection,
    classify_surface_preparation,
    classify_trim_and_doors,
)
from app.plumbing_scope import (
    classify_drain_lines,
    classify_fixture_installation,
    classify_materials,
    classify_permit,
    classify_shutoff_valves,
    classify_supply_lines,
    classify_testing,
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
    detail_fields: tuple[str, ...] = ()


PAINTING = TradeProfile(
    key="painting",
    label="Interior painting",
    scope_labels={
        "walls": "Walls",
        "ceilings": "Ceilings",
        "primer": "Primer",
        "drywall_repair": "Drywall repair",
        "surface_preparation": "Surface preparation",
        "property_protection": "Property protection",
        "trim_and_doors": "Trim and doors",
        "paint_specifications": "Paint specifications",
        "lead_safety": "Lead-safety language",
        "cleanup": "Cleanup",
        "debris_disposal": "Debris disposal",
        "labor_warranty": "Labor warranty",
    },
    classifiers={
        "ceilings": classify_ceilings,
        "walls": classify_walls,
        "primer": classify_primer,
        "drywall_repair": classify_drywall_repair,
        "surface_preparation": classify_surface_preparation,
        "property_protection": classify_property_protection,
        "trim_and_doors": classify_trim_and_doors,
        "paint_specifications": classify_paint_specifications,
        "lead_safety": classify_lead_safety,
        "cleanup": classify_cleanup,
        "debris_disposal": classify_debris_disposal,
        "labor_warranty": classify_labor_warranty,
    },
    risk_descriptions={
        "ceilings": "ceiling painting",
        "primer": "primer",
        "surface_preparation": "surface preparation",
        "property_protection": "protection of floors and fixed property",
        "cleanup": "cleanup",
        "debris_disposal": "debris disposal",
        "labor_warranty": "a labor warranty",
    },
    ai_review_categories=(
        "ceilings",
        "walls",
        "primer",
        "drywall_repair",
        "surface_preparation",
        "property_protection",
        "trim_and_doors",
        "paint_specifications",
        "lead_safety",
        "cleanup",
        "debris_disposal",
        "labor_warranty",
    ),
    detail_fields=("trim_and_doors", "paint_specifications", "lead_safety"),
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
        "moisture_testing": "Moisture testing",
        "waste_allowance": "Waste and order allowance",
        "acclimation": "Material acclimation",
        "furniture_appliances": "Furniture and appliances",
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
        "moisture_testing": classify_moisture_testing,
        "waste_allowance": classify_waste_allowance,
        "acclimation": classify_acclimation,
        "furniture_appliances": classify_furniture_appliances,
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
        "moisture_testing": "subfloor moisture testing",
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
        "moisture_testing",
        "waste_allowance",
        "acclimation",
        "furniture_appliances",
        "transitions",
        "baseboards",
        "cleanup",
        "labor_warranty",
    ),
    detail_fields=(
        "underlayment",
        "moisture_barrier",
        "moisture_testing",
        "waste_allowance",
        "acclimation",
        "furniture_appliances",
        "transitions",
        "baseboards",
    ),
)

PLUMBING = TradeProfile(
    key="plumbing",
    label="Plumbing",
    scope_labels={
        "fixture_installation": "Fixture installation",
        "supply_lines": "Supply lines",
        "drain_lines": "Drain lines",
        "shutoff_valves": "Shutoff valves",
        "permit": "Permit and inspection",
        "materials": "Materials and parts",
        "testing": "Pressure and leak testing",
        "cleanup": "Cleanup",
        "labor_warranty": "Labor warranty",
    },
    classifiers={
        "fixture_installation": classify_fixture_installation,
        "supply_lines": classify_supply_lines,
        "drain_lines": classify_drain_lines,
        "shutoff_valves": classify_shutoff_valves,
        "permit": classify_permit,
        "materials": classify_materials,
        "testing": classify_testing,
        "cleanup": classify_cleanup,
        "labor_warranty": classify_labor_warranty,
    },
    risk_descriptions={
        "supply_lines": "supply-line work",
        "drain_lines": "drain-line work",
        "shutoff_valves": "shutoff valves",
        "permit": "permit and inspection costs",
        "materials": "materials and parts",
        "testing": "pressure or leak testing",
        "cleanup": "cleanup",
        "labor_warranty": "a labor warranty",
    },
    ai_review_categories=(
        "fixture_installation", "supply_lines", "drain_lines", "shutoff_valves",
        "permit", "materials", "testing", "cleanup", "labor_warranty",
    ),
)

TRADE_PROFILES = {profile.key: profile for profile in (PAINTING, FLOORING, PLUMBING)}


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
