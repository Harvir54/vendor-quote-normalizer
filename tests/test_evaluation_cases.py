"""Run curated wording variations as cross-trade extraction regressions."""

import json
import unittest
from pathlib import Path

from app.normalizer import normalize_estimate_text


ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "sample-data" / "evaluation"


class EvaluationCaseTests(unittest.TestCase):
    def test_curated_cases_match_expected_values(self):
        paths = sorted(EVALUATION.glob("*-cases.json"))
        self.assertEqual(len(paths), 4)
        cases = [case for path in paths for case in json.loads(path.read_text())]
        self.assertEqual(len(cases), 12)

        for case in cases:
            with self.subTest(case=case["id"]):
                actual = normalize_estimate_text(case["text"], trade=case["trade"])
                for field, expected in case["expected"].items():
                    if isinstance(expected, dict):
                        for key, value in expected.items():
                            self.assertEqual(actual[field][key], value)
                    else:
                        self.assertEqual(actual[field], expected)

    def test_case_ids_are_unique(self):
        cases = [
            case
            for path in sorted(EVALUATION.glob("*-cases.json"))
            for case in json.loads(path.read_text())
        ]
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
