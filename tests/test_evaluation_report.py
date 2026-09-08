import json
import tempfile
import unittest
from pathlib import Path

from app.evaluation import evaluate_cases


ROOT = Path(__file__).resolve().parents[1]


class EvaluationReportTests(unittest.TestCase):
    def test_reports_current_cross_trade_accuracy(self):
        report = evaluate_cases(ROOT / "sample-data" / "evaluation")
        self.assertEqual(report["cases"], 12)
        self.assertEqual(report["overall"], {"passed": 91, "total": 91, "accuracy": 100.0})
        self.assertEqual(set(report["by_trade"]), {"painting", "flooring", "plumbing", "hvac"})
        self.assertEqual(report["failures"], [])

    def test_reports_actionable_failure_details(self):
        case = [{
            "id": "known-failure",
            "trade": "painting",
            "text": "Example Painting\nESTIMATE TOTAL $100.00\nWalls excluded.",
            "expected": {"walls": {"status": "included"}},
        }]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "painting-cases.json"
            path.write_text(json.dumps(case))
            report = evaluate_cases(Path(directory))

        self.assertEqual(report["overall"]["accuracy"], 0.0)
        self.assertEqual(report["failures"][0]["case_id"], "known-failure")
        self.assertEqual(report["failures"][0]["field"], "walls.status")
        self.assertEqual(report["failures"][0]["expected"], "included")
        self.assertEqual(report["failures"][0]["actual"], "excluded")


if __name__ == "__main__":
    unittest.main()
