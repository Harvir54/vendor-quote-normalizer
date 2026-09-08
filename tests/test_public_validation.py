import unittest
from pathlib import Path

from app.evaluation import evaluate_cases


ROOT = Path(__file__).resolve().parents[1]


class PublicValidationTests(unittest.TestCase):
    def test_anonymized_public_bid_cases_pass(self):
        report = evaluate_cases(ROOT / "sample-data" / "public-validation")
        self.assertEqual(report["cases"], 4)
        self.assertEqual(report["overall"]["passed"], 11)
        self.assertEqual(report["overall"]["total"], 11)
        self.assertEqual(report["overall"]["accuracy"], 100.0)
        self.assertEqual(report["failures"], [])


if __name__ == "__main__":
    unittest.main()
