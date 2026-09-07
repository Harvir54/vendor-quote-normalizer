import unittest
from pathlib import Path

from app.comparison import compare_many_normalized_estimates, compare_normalized_estimates
from app.normalizer import normalize_estimate_text
from app.normalizer import normalize_estimate


ROOT = Path(__file__).resolve().parents[1]


PREMIUM = """Summit Comfort Systems
ESTIMATE TOTAL $14,800.00
Install a 4-ton heat pump and air handler. Manufacturer: Carrier. Outdoor model 25VNA848A003.
Indoor unit model FE4ANF005. AHRI matched system reference included. Rated 18 SEER2, 12 EER2,
and 9 HSPF2. Manual J load calculation included. Modify and seal ductwork. Install thermostat.
New refrigerant line set and condensate drain with float switch included. Electrical disconnect included.
Permit and inspection included. Startup, airflow test, and refrigerant charge verification included.
Remove and dispose of old HVAC equipment. Final cleanup included. Two-year labor warranty.
"""

BASIC = """Inland Air Solutions
ESTIMATE TOTAL $11,900.00
Install a 3.5-ton heat pump and air handler, rated 15.2 SEER2 and 7.8 HSPF2.
Existing ductwork and refrigerant line set will be reused. Thermostat included.
Permit included. Startup and system testing included. Old equipment disposal included.
Manual J load calculation not included. AHRI certificate not included. Electrical work excluded.
One-year labor warranty. Cleanup included.
"""


class HVACTests(unittest.TestCase):
    def test_normalizes_generated_hvac_pdf(self):
        estimate = normalize_estimate(
            ROOT / "sample-data" / "quotes" / "synthetic-hvac-estimate-summit.pdf",
            trade="hvac",
        )
        self.assertEqual(estimate["vendor_name"], "SUMMIT COMFORT SYSTEMS")
        self.assertEqual(estimate["estimate_total"], "$14,800.00")
        self.assertEqual(estimate["hvac_system"]["capacity_tons"], 4)

    def test_extracts_system_capacity_efficiency_and_models(self):
        estimate = normalize_estimate_text(PREMIUM, trade="hvac")
        self.assertIn("heat pump", estimate["hvac_system"]["system_types"])
        self.assertEqual(estimate["hvac_system"]["capacity_tons"], 4)
        self.assertEqual(estimate["hvac_efficiency"]["seer2"], 18)
        self.assertEqual(estimate["hvac_efficiency"]["hspf2"], 9)
        self.assertIn("25VNA848A003", estimate["hvac_equipment"]["model_numbers"])
        self.assertEqual(estimate["matched_system"]["status"], "included")
        self.assertEqual(estimate["commissioning"]["status"], "included")

    def test_converts_btu_capacity_to_tons(self):
        estimate = normalize_estimate_text(
            "Install a 36,000 BTUH ductless mini-split heat pump.", trade="hvac"
        )
        self.assertEqual(estimate["hvac_system"]["capacity_tons"], 3)
        self.assertIn("ductless mini-split", estimate["hvac_system"]["system_types"])

    def test_flags_capacity_efficiency_and_missing_quality_items(self):
        comparison = compare_normalized_estimates(
            normalize_estimate_text(PREMIUM, trade="hvac"),
            normalize_estimate_text(BASIC, trade="hvac"),
            trade="hvac",
        )
        codes = {flag["code"] for flag in comparison["risk_flags"]}
        self.assertIn("HVAC_CAPACITY_MISMATCH", codes)
        self.assertIn("LOWER_SEER2", codes)
        self.assertIn("LOAD_CALCULATION_EXCLUDED", codes)
        self.assertIn("MATCHED_SYSTEM_EXCLUDED", codes)
        self.assertIn("ELECTRICAL_EXCLUDED", codes)

    def test_flags_system_type_mismatch_across_multiple_bids(self):
        air_conditioner = normalize_estimate_text(
            "Install a 3-ton central air conditioner.", trade="hvac"
        )
        heat_pump = normalize_estimate_text(
            "Install a 3-ton heat pump.", trade="hvac"
        )
        comparison = compare_many_normalized_estimates(
            [air_conditioner, heat_pump], trade="hvac"
        )
        codes = {flag["code"] for flag in comparison["risk_flags"]}
        self.assertIn("HVAC_SYSTEM_TYPE_MISMATCH", codes)


if __name__ == "__main__":
    unittest.main()
