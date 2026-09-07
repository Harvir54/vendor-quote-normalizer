import unittest

from app.normalizer import normalize_estimate_text
from app.painting_scope import (
    classify_lead_safety,
    classify_paint_specifications,
    classify_property_protection,
    classify_surface_preparation,
    classify_trim_and_doors,
)


class PaintingDetailTests(unittest.TestCase):
    def test_extracts_preparation_protection_and_trim(self):
        text = (
            "Protect flooring and fixtures with plastic and drop cloths. "
            "Surface preparation includes filling nail holes and sanding repairs. "
            "Paint baseboards, door casings, and five interior doors."
        )

        self.assertEqual(classify_property_protection(text)["status"], "included")
        self.assertEqual(classify_surface_preparation(text)["status"], "included")
        self.assertEqual(classify_trim_and_doors(text)["status"], "included")

    def test_extracts_product_manufacturer_and_sheen(self):
        result = classify_paint_specifications(
            "Apply Sherwin-Williams Duration Home eggshell acrylic paint."
        )

        self.assertEqual(result["status"], "included")
        self.assertEqual(result["manufacturer"], "Sherwin-Williams")
        self.assertEqual(result["product_line"], "Duration Home")
        self.assertEqual(result["sheens"], ["eggshell"])

    def test_does_not_infer_missing_paint_specification(self):
        result = classify_paint_specifications("Apply two coats to all walls.")

        self.assertEqual(result["status"], "not_stated")
        self.assertIsNone(result["manufacturer"])
        self.assertEqual(result["sheens"], [])

    def test_classifies_excluded_lead_work(self):
        result = classify_lead_safety("Lead testing and abatement are excluded.")

        self.assertEqual(result["status"], "excluded")

    def test_painting_profile_includes_detail_fields(self):
        estimate = normalize_estimate_text(
            "ACME\nESTIMATE\nPrep and paint walls with premium eggshell paint. "
            "Protect floors with drop cloths.",
            trade="painting",
        )

        self.assertIn("surface_preparation", estimate)
        self.assertIn("property_protection", estimate)
        self.assertIn("paint_specifications", estimate)
