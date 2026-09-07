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
    classify_access_restoration,
    classify_camera_inspection,
    classify_drain_lines,
    classify_excavation,
    classify_fixture_installation,
    classify_materials,
    classify_permit,
    classify_plumbing_project,
    classify_removal_disposal,
    classify_shutoff_valves,
    classify_supply_lines,
    classify_testing,
    classify_water_heater,
)
from app.hvac_scope import (
    classify_commissioning as classify_hvac_commissioning,
    classify_condensate,
    classify_ductwork,
    classify_electrical,
    classify_hvac_efficiency,
    classify_hvac_equipment,
    classify_hvac_system,
    classify_load_calculation,
    classify_matched_system,
    classify_permit as classify_hvac_permit,
    classify_refrigerant_lines,
    classify_removal_disposal as classify_hvac_removal_disposal,
    classify_thermostat,
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
        "plumbing_project": "Plumbing project type",
        "fixture_installation": "Fixture installation",
        "supply_lines": "Supply lines",
        "drain_lines": "Drain lines",
        "shutoff_valves": "Shutoff valves",
        "permit": "Permit and inspection",
        "materials": "Materials and parts",
        "testing": "Pressure and leak testing",
        "water_heater": "Water-heater specifications",
        "removal_disposal": "Existing equipment removal",
        "access_restoration": "Access and surface restoration",
        "camera_inspection": "Camera inspection",
        "excavation": "Excavation and backfill",
        "cleanup": "Cleanup",
        "labor_warranty": "Labor warranty",
    },
    classifiers={
        "plumbing_project": classify_plumbing_project,
        "fixture_installation": classify_fixture_installation,
        "supply_lines": classify_supply_lines,
        "drain_lines": classify_drain_lines,
        "shutoff_valves": classify_shutoff_valves,
        "permit": classify_permit,
        "materials": classify_materials,
        "testing": classify_testing,
        "water_heater": classify_water_heater,
        "removal_disposal": classify_removal_disposal,
        "access_restoration": classify_access_restoration,
        "camera_inspection": classify_camera_inspection,
        "excavation": classify_excavation,
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
        "removal_disposal": "removal and disposal of existing equipment",
        "access_restoration": "repair of opened walls, floors, or other surfaces",
        "cleanup": "cleanup",
        "labor_warranty": "a labor warranty",
    },
    ai_review_categories=(
        "plumbing_project", "fixture_installation", "supply_lines", "drain_lines",
        "shutoff_valves", "permit", "materials", "testing", "water_heater",
        "removal_disposal", "access_restoration", "camera_inspection",
        "excavation", "cleanup", "labor_warranty",
    ),
    detail_fields=(
        "water_heater",
        "removal_disposal",
        "access_restoration",
        "camera_inspection",
        "excavation",
    ),
)

HVAC = TradeProfile(
    key="hvac",
    label="HVAC",
    scope_labels={
        "hvac_system": "System type and capacity",
        "hvac_equipment": "Equipment and model numbers",
        "hvac_efficiency": "Efficiency ratings",
        "ductwork": "Ductwork",
        "thermostat": "Thermostat and controls",
        "permit": "Permit and inspection",
        "commissioning": "Startup and system testing",
        "removal_disposal": "Old equipment removal",
        "load_calculation": "Load calculation and sizing",
        "matched_system": "AHRI matched-system documentation",
        "electrical": "Electrical work",
        "refrigerant_lines": "Refrigerant line set",
        "condensate": "Condensate drainage and protection",
        "cleanup": "Cleanup",
        "labor_warranty": "Labor warranty",
    },
    classifiers={
        "hvac_system": classify_hvac_system,
        "hvac_equipment": classify_hvac_equipment,
        "hvac_efficiency": classify_hvac_efficiency,
        "ductwork": classify_ductwork,
        "thermostat": classify_thermostat,
        "permit": classify_hvac_permit,
        "commissioning": classify_hvac_commissioning,
        "removal_disposal": classify_hvac_removal_disposal,
        "load_calculation": classify_load_calculation,
        "matched_system": classify_matched_system,
        "electrical": classify_electrical,
        "refrigerant_lines": classify_refrigerant_lines,
        "condensate": classify_condensate,
        "cleanup": classify_cleanup,
        "labor_warranty": classify_labor_warranty,
    },
    risk_descriptions={
        "ductwork": "needed ductwork",
        "thermostat": "a thermostat or controls",
        "permit": "permit and inspection costs",
        "commissioning": "system startup and performance testing",
        "removal_disposal": "removal and disposal of old equipment",
        "load_calculation": "a documented load calculation",
        "matched_system": "AHRI matched-system documentation",
        "electrical": "required electrical work",
        "refrigerant_lines": "refrigerant line-set work",
        "condensate": "condensate drainage and protection",
        "cleanup": "cleanup",
        "labor_warranty": "a labor warranty",
    },
    ai_review_categories=(
        "hvac_system", "hvac_equipment", "hvac_efficiency", "ductwork",
        "thermostat", "permit", "commissioning", "removal_disposal",
        "load_calculation", "matched_system", "electrical",
        "refrigerant_lines", "condensate", "cleanup", "labor_warranty",
    ),
    detail_fields=(
        "hvac_equipment", "hvac_efficiency", "load_calculation",
        "matched_system", "electrical", "refrigerant_lines", "condensate",
    ),
)

TRADE_PROFILES = {
    profile.key: profile for profile in (PAINTING, FLOORING, PLUMBING, HVAC)
}


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
