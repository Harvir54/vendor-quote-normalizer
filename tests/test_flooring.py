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
        self.assertEqual(estimate["existing_floor_removal"]["status"], "included")
        self.assertEqual(estimate["baseboards"]["status"], "excluded")

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


if __name__ == "__main__":
    unittest.main()
