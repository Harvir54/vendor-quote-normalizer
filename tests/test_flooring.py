import unittest

from app.comparison import compare_normalized_estimates
from app.normalizer import normalize_estimate_text


PACIFIC = """Pacific Floorworks
ESTIMATE TOTAL $8,640.00
Remove and dispose of existing carpet and pad.
Minor subfloor preparation and leveling included.
Install 1,200 sq ft luxury vinyl plank, 6.5 mm thickness, 20 mil wear layer, with attached pad.
Moisture barrier and transition strips included. Final cleanup included.
Baseboards are excluded. Two-year labor warranty included.
Floating click-lock installation. Moisture testing included.
Material order 1,320 sq ft includes 10% waste overage. Furniture moving is included.
"""
VALLEY = """Valley Flooring Group
ESTIMATE TOTAL $7,150.00
Install 1,100 sq ft LVP flooring with 12 mil wear layer.
Transition strips included. Final cleanup included.
Existing flooring removal is not included.
Subfloor repair or leveling, if needed, will be priced separately.
Underlayment is not stated. Moisture barrier is not stated.
Baseboard work is not stated. One-year labor warranty included.
"""


class FlooringTests(unittest.TestCase):
    def test_extracts_flooring_metrics_and_scope(self):
        estimate = normalize_estimate_text(PACIFIC, trade="flooring")
        installation = estimate["flooring_installation"]
        self.assertEqual(installation["area_sq_ft"], 1200)
        self.assertEqual(installation["material_type"], "luxury vinyl plank")
        self.assertEqual(installation["wear_layer_mil"], 20)
        self.assertEqual(installation["thickness_mm"], 6.5)
        self.assertEqual(
            installation["installation_method"],
            "floating / click-lock",
        )
        self.assertEqual(estimate["existing_floor_removal"]["status"], "included")
        self.assertEqual(estimate["baseboards"]["status"], "excluded")
        self.assertEqual(estimate["moisture_testing"]["status"], "included")
        self.assertEqual(estimate["waste_allowance"]["waste_percent"], 10.0)
        self.assertEqual(estimate["waste_allowance"]["material_order_sq_ft"], 1320)
        self.assertEqual(estimate["furniture_appliances"]["status"], "included")

    def test_extracts_material_specific_installation_method(self):
        estimate = normalize_estimate_text(
            "Install 900 sq ft engineered hardwood using a glue-down installation.",
            trade="flooring",
        )

        self.assertEqual(
            estimate["flooring_installation"]["installation_method"],
            "glue-down",
        )

    def test_does_not_confuse_debris_with_material_waste_allowance(self):
        estimate = normalize_estimate_text(
            "Install flooring. Construction waste disposal included.",
            trade="flooring",
        )

        self.assertEqual(estimate["waste_allowance"]["status"], "not_stated")

    def test_customer_furniture_responsibility_is_not_contractor_scope(self):
        estimate = normalize_estimate_text(
            "Customer must move all furniture before installation.",
            trade="flooring",
        )

        self.assertEqual(estimate["furniture_appliances"]["status"], "excluded")

    def test_flags_area_product_and_scope_differences(self):
        comparison = compare_normalized_estimates(
            normalize_estimate_text(PACIFIC, trade="flooring"),
            normalize_estimate_text(VALLEY, trade="flooring"),
            trade="flooring",
        )
        codes = {flag["code"] for flag in comparison["risk_flags"]}
        self.assertIn("FLOOR_AREA_MISMATCH", codes)
        self.assertIn("LOWER_WEAR_LAYER", codes)
        self.assertIn("EXISTING_FLOOR_REMOVAL_EXCLUDED", codes)
        self.assertIn("SUBFLOOR_PREPARATION_UNCLEAR", codes)
        self.assertIn("SHORTER_LABOR_WARRANTY", codes)
        self.assertIn("MOISTURE_TESTING_NOT_STATED", codes)
        self.assertEqual(comparison["vendors"][0]["unit_price_cents"], 720)
        self.assertEqual(comparison["vendors"][1]["unit_price_cents"], 650)
        self.assertEqual(comparison["vendors"][0]["unit_label"], "per sq ft")


if __name__ == "__main__":
    unittest.main()
