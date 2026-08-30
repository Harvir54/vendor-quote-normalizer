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
                "ceilings": {"status": "not_stated", "evidence": None},
                "walls": {
                    "status": "included",
                    "evidence": "Paint walls: $500.00",
                    "coat_count": None,
                },
                "primer": {"status": "not_stated", "evidence": None},
                "drywall_repair": {
                    "status": "not_stated",
                    "evidence": None,
                    "limitations": [],
                },
                "cleanup": {"status": "not_stated", "evidence": None},
                "debris_disposal": {"status": "not_stated", "evidence": None},
                "labor_warranty": {
                    "status": "not_stated",
                    "evidence": None,
                    "duration_years": None,
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


if __name__ == "__main__":
    unittest.main()
