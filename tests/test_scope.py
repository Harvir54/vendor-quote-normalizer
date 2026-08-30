import unittest
from pathlib import Path

from app.pdf_text import extract_pdf_text
from app.scope import classify_ceilings, classify_primer, classify_walls


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


class WallScopeTests(unittest.TestCase):
    def test_classifies_two_wall_coats(self):
        result = classify_walls("Apply two finish coats to all apartment walls.")
        self.assertEqual(result["status"], "included")
        self.assertEqual(result["coat_count"], 2)

    def test_finds_coat_count_in_following_sentence(self):
        result = classify_walls(
            "Prep and paint apartment walls. One finish coat throughout."
        )
        self.assertEqual(result["status"], "included")
        self.assertEqual(result["coat_count"], 1)
        self.assertEqual(
            result["evidence"],
            "Prep and paint apartment walls. One finish coat throughout.",
        )

    def test_allows_included_walls_without_a_coat_count(self):
        result = classify_walls("Paint all walls in the apartment.")
        self.assertEqual(result["status"], "included")
        self.assertIsNone(result["coat_count"])

    def test_classifies_excluded_walls(self):
        result = classify_walls("Garage walls are excluded.")
        self.assertEqual(result["status"], "excluded")
        self.assertIsNone(result["coat_count"])

    def test_classifies_conditional_walls_as_unclear(self):
        result = classify_walls("Accent walls may be painted if requested.")
        self.assertEqual(result["status"], "unclear")

    def test_classifies_missing_wall_language_as_not_stated(self):
        self.assertEqual(
            classify_walls("Paint five interior doors."),
            {"status": "not_stated", "evidence": None, "coat_count": None},
        )

    def test_classifies_sample_wall_scope_and_coat_counts(self):
        blue_oak = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        )
        inland_pro = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf"
        )
        self.assertEqual(classify_walls(blue_oak)["coat_count"], 2)
        inland_result = classify_walls(inland_pro)
        self.assertEqual(inland_result["coat_count"], 1)
        self.assertIn("one finish coat throughout.", inland_result["evidence"])


class PrimerScopeTests(unittest.TestCase):
    def test_classifies_spot_primer_as_included(self):
        result = classify_primer(
            "Spot-prime all repaired areas with stain-blocking primer."
        )
        self.assertEqual(result["status"], "included")
        self.assertEqual(
            result["evidence"],
            "Spot-prime all repaired areas with stain-blocking primer.",
        )

    def test_classifies_excluded_primer(self):
        result = classify_primer("Primer is not included in this estimate.")
        self.assertEqual(result["status"], "excluded")

    def test_classifies_unspecified_primer_as_not_stated(self):
        result = classify_primer("Primer terms are not specified.")
        self.assertEqual(result["status"], "not_stated")
        self.assertEqual(result["evidence"], "Primer terms are not specified.")

    def test_classifies_conditional_primer_as_unclear(self):
        result = classify_primer("Primer may be applied if needed.")
        self.assertEqual(result["status"], "unclear")

    def test_classifies_missing_primer_language_as_not_stated(self):
        self.assertEqual(
            classify_primer("Apply two coats to all walls."),
            {"status": "not_stated", "evidence": None},
        )

    def test_classifies_sample_primer_scope(self):
        blue_oak = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        )
        inland_pro = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf"
        )
        blue_result = classify_primer(blue_oak)
        inland_result = classify_primer(inland_pro)
        self.assertEqual(blue_result["status"], "included")
        self.assertIn("Spot-prime", blue_result["evidence"])
        self.assertEqual(inland_result["status"], "not_stated")
        self.assertIn("not specified", inland_result["evidence"])


if __name__ == "__main__":
    unittest.main()
