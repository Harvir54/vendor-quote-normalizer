import unittest
from pathlib import Path

from app.pdf_text import PdfExtractionError, extract_pdf_text


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"


class PdfTextTests(unittest.TestCase):
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
