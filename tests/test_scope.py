import unittest
from pathlib import Path

from app.pdf_text import extract_pdf_text
from app.scope import classify_ceilings


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"


class CeilingScopeTests(unittest.TestCase):
    def test_classifies_included_ceiling_work(self):
        result = classify_ceilings(
            "Apply one finish coat to all ceilings, including bathroom ceiling."
        )
        self.assertEqual(result["status"], "included")
        self.assertEqual(
            result["evidence"],
            "Apply one finish coat to all ceilings, including bathroom ceiling.",
        )

    def test_classifies_excluded_ceiling_work(self):
        result = classify_ceilings("Ceilings are not included.")
        self.assertEqual(
            result,
            {"status": "excluded", "evidence": "Ceilings are not included."},
        )

    def test_classifies_missing_ceiling_language_as_not_stated(self):
        self.assertEqual(
            classify_ceilings("Paint all apartment walls."),
            {"status": "not_stated", "evidence": None},
        )

    def test_classifies_conditional_ceiling_work_as_unclear(self):
        result = classify_ceilings("Ceilings may be painted if requested.")
        self.assertEqual(result["status"], "unclear")
        self.assertEqual(result["evidence"], "Ceilings may be painted if requested.")

    def test_classifies_sample_estimates(self):
        blue_oak = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        )
        inland_pro = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf"
        )
        self.assertEqual(classify_ceilings(blue_oak)["status"], "included")
        self.assertEqual(classify_ceilings(inland_pro)["status"], "excluded")


if __name__ == "__main__":
    unittest.main()
