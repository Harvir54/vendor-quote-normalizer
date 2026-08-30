import unittest
from pathlib import Path

from app.pdf_text import (
    PdfExtractionError,
    extract_pdf_text,
    find_estimate_total,
    find_money_values,
)


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"


class PdfTextTests(unittest.TestCase):
    def test_finds_multiple_money_values(self):
        text = "Repair is $550.00 and the total is $4,750.00"
        self.assertEqual(find_money_values(text), ["$550.00", "$4,750.00"])

    def test_returns_empty_list_when_no_money_is_found(self):
        self.assertEqual(find_money_values("No price is listed."), [])

    def test_finds_labeled_estimate_total(self):
        text = "Repair: $550.00\nESTIMATE TOTAL\n$4,750.00"
        self.assertEqual(find_estimate_total(text), "$4,750.00")

    def test_returns_none_when_total_is_missing(self):
        self.assertIsNone(find_estimate_total("No final price is provided"))

    def test_finds_total_in_both_sample_estimates(self):
        blue_oak = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        )
        inland_pro = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf"
        )
        self.assertEqual(find_estimate_total(blue_oak), "$4,750.00")
        self.assertEqual(find_estimate_total(inland_pro), "$3,890.00")

    def test_extracts_blue_oak_text(self):
        text = extract_pdf_text(QUOTES / "synthetic-painting-estimate-blue-oak.pdf")
        self.assertIn("Blue Oak Painting Co.", text)
        self.assertIn("$4,750.00", text)
        self.assertIn("Two-year labor warranty", text)

    def test_extracts_inland_pro_text(self):
        text = extract_pdf_text(QUOTES / "synthetic-painting-estimate-inland-pro.pdf")
        self.assertIn("Inland Pro Paint & Repair", text)
        self.assertIn("$3,890.00", text)
        self.assertIn("Ceilings are not included", text)

    def test_rejects_missing_file(self):
        with self.assertRaises(PdfExtractionError):
            extract_pdf_text(QUOTES / "missing.pdf")

    def test_rejects_non_pdf_file(self):
        with self.assertRaises(PdfExtractionError):
            extract_pdf_text(ROOT / "README.md")


if __name__ == "__main__":
    unittest.main()
