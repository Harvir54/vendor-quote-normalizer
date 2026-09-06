import unittest
from pathlib import Path

from app.normalizer import normalize_estimate, normalize_estimate_text


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"


class NormalizerTests(unittest.TestCase):
    def test_normalizes_estimate_text(self):
        text = (
            "Example Painting Co.\n"
            "ESTIMATE\n"
            "Paint walls: $500.00\n"
            "ESTIMATE TOTAL\n"
            "$2,000.00"
        )
        self.assertEqual(
            normalize_estimate_text(text),
            {
                "vendor_name": "Example Painting Co.",
                "estimate_total": "$2,000.00",
                "all_money_values": ["$500.00", "$2,000.00"],
                "ceilings": {"status": "not_stated", "evidence": None, "source": "rule", "confidence": 0.70, "review_required": True},
                "walls": {
                    "status": "included",
                    "evidence": "Paint walls: $500.00",
                    "coat_count": None,
                    "source": "rule",
                    "confidence": 0.95,
                    "review_required": False,
                },
                "primer": {"status": "not_stated", "evidence": None, "source": "rule", "confidence": 0.70, "review_required": True},
                "drywall_repair": {
                    "status": "not_stated",
                    "evidence": None,
                    "limitations": [],
                    "source": "rule",
                    "confidence": 0.70,
                    "review_required": True,
                },
                "cleanup": {"status": "not_stated", "evidence": None, "source": "rule", "confidence": 0.70, "review_required": True},
                "debris_disposal": {"status": "not_stated", "evidence": None, "source": "rule", "confidence": 0.70, "review_required": True},
                "labor_warranty": {
                    "status": "not_stated",
                    "evidence": None,
                    "duration_years": None,
                    "source": "rule",
                    "confidence": 0.70,
                    "review_required": True,
                },
            },
        )

    def test_normalizes_blue_oak_pdf(self):
        result = normalize_estimate(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        )
        self.assertEqual(result["vendor_name"], "Blue Oak Painting Co.")
        self.assertEqual(result["estimate_total"], "$4,750.00")
        self.assertIn("$300.00", result["all_money_values"])
        self.assertEqual(result["ceilings"]["status"], "included")
        self.assertEqual(result["walls"]["status"], "included")
        self.assertEqual(result["walls"]["coat_count"], 2)
        self.assertEqual(result["primer"]["status"], "included")
        self.assertEqual(result["drywall_repair"]["status"], "included")
        self.assertEqual(result["cleanup"]["status"], "included")
        self.assertEqual(result["debris_disposal"]["status"], "included")
        self.assertEqual(result["labor_warranty"]["duration_years"], 2)

    def test_normalizes_inland_pro_pdf(self):
        result = normalize_estimate(
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf"
        )
        self.assertEqual(result["vendor_name"], "Inland Pro Paint & Repair")
        self.assertEqual(result["estimate_total"], "$3,890.00")
        self.assertIn("$220.00", result["all_money_values"])
        self.assertEqual(result["ceilings"]["status"], "excluded")
        self.assertEqual(result["walls"]["status"], "included")
        self.assertEqual(result["walls"]["coat_count"], 1)
        self.assertEqual(result["primer"]["status"], "not_stated")
        self.assertEqual(result["drywall_repair"]["status"], "included")
        self.assertTrue(result["drywall_repair"]["limitations"])
        self.assertEqual(result["cleanup"]["status"], "not_stated")
        self.assertEqual(result["debris_disposal"]["status"], "not_stated")
        self.assertEqual(result["labor_warranty"]["status"], "not_stated")

    def test_normalizes_canyon_view_pdf(self):
        result = normalize_estimate(
            QUOTES / "synthetic-painting-proposal-canyon-view.pdf"
        )
        self.assertEqual(result["vendor_name"], "CANYON VIEW COATINGS")
        self.assertEqual(result["estimate_total"], "$4,400.00")
        self.assertIn("$4,570.00", result["all_money_values"])
        self.assertEqual(result["ceilings"]["status"], "partial")
        self.assertEqual(result["walls"]["status"], "included")
        self.assertEqual(result["walls"]["coat_count"], 2)
        self.assertEqual(result["primer"]["status"], "included")
        self.assertEqual(result["drywall_repair"]["status"], "included")
        self.assertTrue(result["drywall_repair"]["limitations"])
        self.assertEqual(result["cleanup"]["status"], "included")
        self.assertEqual(result["debris_disposal"]["status"], "included")
        self.assertEqual(result["labor_warranty"]["status"], "included")
        self.assertEqual(result["labor_warranty"]["duration_years"], 1)

    def test_every_scope_item_reports_source_and_confidence(self):
        result = normalize_estimate(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        )
        fields = (
            "ceilings",
            "walls",
            "primer",
            "drywall_repair",
            "cleanup",
            "debris_disposal",
            "labor_warranty",
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(result[field]["source"], "rule")
                self.assertGreaterEqual(result[field]["confidence"], 0)
                self.assertLessEqual(result[field]["confidence"], 1)

    def test_routes_unrecognized_wording_for_review(self):
        result = normalize_estimate_text(
            "Example Painting Co.\n"
            "Seal repaired areas before finish application.\n"
            "Leave the premises broom clean at completion.\n"
            "All waste generated by our crew will be taken off site.\n"
            "We stand behind our workmanship for twelve months.\n"
            "ESTIMATE TOTAL $2,000.00"
        )
        for field in ("primer", "cleanup", "debris_disposal", "labor_warranty"):
            with self.subTest(field=field):
                self.assertTrue(result[field]["review_required"])
                self.assertEqual(result[field]["source"], "rule")

    def test_keeps_clear_rule_matches_out_of_review_queue(self):
        result = normalize_estimate_text(
            "Cleanup is included. Debris disposal is included. "
            "One-year labor warranty included. ESTIMATE TOTAL $2,000.00"
        )
        for field in ("cleanup", "debris_disposal", "labor_warranty"):
            with self.subTest(field=field):
                self.assertFalse(result[field]["review_required"])


if __name__ == "__main__":
    unittest.main()
