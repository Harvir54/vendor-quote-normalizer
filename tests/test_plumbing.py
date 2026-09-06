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


if __name__ == "__main__":
    unittest.main()
