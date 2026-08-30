import unittest
from pathlib import Path

from app.comparison import compare_estimates, money_to_cents


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = compare_estimates(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf",
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf",
        )

    def test_converts_money_to_cents(self):
        self.assertEqual(money_to_cents("$4,750.00"), 475000)
        self.assertEqual(money_to_cents("$0.00"), 0)
        self.assertIsNone(money_to_cents(None))

    def test_compares_vendor_prices(self):
        self.assertEqual(self.result["price_difference_cents"], 86000)
        self.assertEqual(self.result["lower_bidder"], "Inland Pro Paint & Repair")
        self.assertEqual(self.result["vendors"][0]["total_cents"], 475000)
        self.assertEqual(self.result["vendors"][1]["total_cents"], 389000)

    def test_builds_scope_matrix(self):
        matrix = self.result["scope_comparison"]
        self.assertEqual(matrix["walls"]["first"]["coat_count"], 2)
        self.assertEqual(matrix["walls"]["second"]["coat_count"], 1)
        self.assertEqual(matrix["ceilings"]["first"]["status"], "included")
        self.assertEqual(matrix["ceilings"]["second"]["status"], "excluded")

    def test_generates_expected_risk_flags(self):
        flags = {flag["code"]: flag for flag in self.result["risk_flags"]}
        expected = {
            "FEWER_WALL_COATS",
            "CEILINGS_EXCLUDED",
            "PRIMER_NOT_STATED",
            "CLEANUP_NOT_STATED",
            "DEBRIS_DISPOSAL_NOT_STATED",
            "LABOR_WARRANTY_NOT_STATED",
        }
        self.assertEqual(set(flags), expected)
        self.assertTrue(all(flag["evidence"] for flag in flags.values()))
        self.assertEqual(
            flags["CEILINGS_EXCLUDED"]["vendor_name"],
            "Inland Pro Paint & Repair",
        )


if __name__ == "__main__":
    unittest.main()
