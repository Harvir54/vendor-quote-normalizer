import unittest

from app.comparison import compare_normalized_estimates
from app.normalizer import normalize_estimate_text


COMPLETE = """ClearFlow Plumbing
ESTIMATE TOTAL $4,980.00
Install 4 customer-supplied plumbing fixtures. Replace supply lines and shutoff valves.
Drain line modifications included. Materials and parts included. Permit and inspection fees included.
Pressure testing and leak testing included. Final cleanup included. Two-year labor warranty included.
"""
LIMITED = """Rapid Rooter Services
ESTIMATE TOTAL $3,900.00
Install 3 customer-supplied plumbing fixtures. Supply lines included.
Drain line modifications are not included. Shutoff valves if needed cost extra.
Permit fees are not included. Materials and parts included. Leak testing included.
Cleanup included. One-year labor warranty included.
"""


class PlumbingTests(unittest.TestCase):
    def test_extracts_fixture_count_and_scope(self):
        estimate = normalize_estimate_text(COMPLETE, trade="plumbing")
        self.assertEqual(estimate["fixture_installation"]["fixture_count"], 4)
        self.assertEqual(
            estimate["plumbing_project"]["project_types"],
            ["fixture replacement"],
        )
        self.assertEqual(estimate["permit"]["status"], "included")
        self.assertEqual(estimate["testing"]["status"], "included")

    def test_flags_fixture_count_and_exclusions(self):
        comparison = compare_normalized_estimates(
            normalize_estimate_text(COMPLETE, trade="plumbing"),
            normalize_estimate_text(LIMITED, trade="plumbing"),
            trade="plumbing",
        )
        codes = {flag["code"] for flag in comparison["risk_flags"]}
        self.assertIn("FIXTURE_COUNT_MISMATCH", codes)
        self.assertIn("DRAIN_LINES_EXCLUDED", codes)
        self.assertIn("PERMIT_EXCLUDED", codes)
        self.assertIn("SHORTER_LABOR_WARRANTY", codes)
        self.assertEqual(comparison["vendors"][0]["unit_price_cents"], 124500)
        self.assertEqual(comparison["vendors"][1]["unit_price_cents"], 130000)
        self.assertEqual(comparison["vendors"][0]["unit_label"], "per fixture")

    def test_extracts_water_heater_details(self):
        estimate = normalize_estimate_text(
            "Apex Plumbing\nReplace existing unit with a 50-gallon natural gas water heater. "
            "Remove and dispose of old water heater.",
            trade="plumbing",
        )
        self.assertEqual(estimate["plumbing_project"]["project_types"], ["water heater"])
        self.assertFalse(estimate["water_heater"]["tankless"])
        self.assertEqual(estimate["water_heater"]["capacity_gallons"], 50)
        self.assertEqual(estimate["water_heater"]["fuel_type"], "natural gas")
        self.assertEqual(estimate["removal_disposal"]["status"], "included")

    def test_extracts_tankless_and_repipe_projects(self):
        tankless = normalize_estimate_text(
            "Install an electric tankless water heater.", trade="plumbing"
        )
        repipe = normalize_estimate_text(
            "Complete whole-house piping replacement and repipe.", trade="plumbing"
        )
        self.assertTrue(tankless["water_heater"]["tankless"])
        self.assertEqual(tankless["water_heater"]["fuel_type"], "electric")
        self.assertIn("repipe", repipe["plumbing_project"]["project_types"])

    def test_treats_owner_restoration_as_excluded_vendor_scope(self):
        estimate = normalize_estimate_text(
            "Drywall patch and restoration by owner after plumbing access.",
            trade="plumbing",
        )
        self.assertEqual(estimate["access_restoration"]["status"], "excluded")

    def test_flags_different_plumbing_project_types(self):
        fixture_bid = normalize_estimate_text(
            "Alpha Plumbing\nInstall 2 plumbing fixtures. Total $1,000.00",
            trade="plumbing",
        )
        sewer_bid = normalize_estimate_text(
            "Beta Plumbing\nSewer line replacement included. Total $2,000.00",
            trade="plumbing",
        )
        comparison = compare_normalized_estimates(
            fixture_bid, sewer_bid, trade="plumbing"
        )
        codes = {flag["code"] for flag in comparison["risk_flags"]}
        self.assertIn("PLUMBING_PROJECT_TYPE_MISMATCH", codes)


if __name__ == "__main__":
    unittest.main()
