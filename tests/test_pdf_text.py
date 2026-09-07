import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from pypdf import PdfWriter

from app.pdf_text import (
    PdfExtractionError,
    extract_pdf_text,
    find_estimate_total,
    find_money_values,
    find_vendor_name,
)


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"


class PdfTextTests(unittest.TestCase):
    def test_uses_ocr_fallback_for_image_only_pdf(self):
        class FakeTranscriber:
            def __init__(self):
                self.paths = []

            def transcribe_pdf(self, pdf_path):
                self.paths.append(pdf_path)
                return "SCANNED QUOTE\nESTIMATE TOTAL $1,250.00"

        with NamedTemporaryFile(suffix=".pdf") as temporary_pdf:
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            writer.write(temporary_pdf)
            temporary_pdf.flush()
            transcriber = FakeTranscriber()

            text = extract_pdf_text(Path(temporary_pdf.name), transcriber)

        self.assertIn("SCANNED QUOTE", text)
        self.assertEqual(transcriber.paths, [Path(temporary_pdf.name)])

    def test_scanned_pdf_explains_how_to_enable_ocr(self):
        with NamedTemporaryFile(suffix=".pdf") as temporary_pdf:
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            writer.write(temporary_pdf)
            temporary_pdf.flush()

            with self.assertRaisesRegex(PdfExtractionError, "OPENAI_API_KEY"):
                extract_pdf_text(Path(temporary_pdf.name))

    def test_finds_multiple_money_values(self):
        text = "Repair is $550.00 and the total is $4,750.00"
        self.assertEqual(find_money_values(text), ["$550.00", "$4,750.00"])

    def test_returns_empty_list_when_no_money_is_found(self):
        self.assertEqual(find_money_values("No price is listed."), [])

    def test_finds_labeled_estimate_total(self):
        text = "Repair: $550.00\nESTIMATE TOTAL\n$4,750.00"
        self.assertEqual(find_estimate_total(text), "$4,750.00")

    def test_finds_labeled_proposal_total_after_subtotal_and_discount(self):
        text = (
            "Subtotal\n$4,570.00\n"
            "Customer loyalty discount\n-$170.00\n"
            "PROPOSAL TOTAL\n$4,400.00"
        )
        self.assertEqual(find_estimate_total(text), "$4,400.00")

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

    def test_finds_vendor_before_document_label(self):
        text = "Blue Oak Painting Co.\nESTIMATE\nTotal: $4,750.00"
        self.assertEqual(find_vendor_name(text), "Blue Oak Painting Co.")

    def test_vendor_label_matching_ignores_case_and_blank_lines(self):
        text = "Inland Pro Paint & Repair\n\nproposal\n$3,890.00"
        self.assertEqual(find_vendor_name(text), "Inland Pro Paint & Repair")

    def test_vendor_skips_descriptive_subtitle_before_proposal_label(self):
        text = (
            "CANYON VIEW COATINGS\n"
            "Interior repaint proposal | Licensed and insured\n"
            "PROPOSAL\n"
            "CV-1048"
        )
        self.assertEqual(find_vendor_name(text), "CANYON VIEW COATINGS")

    def test_vendor_skips_other_proposal_subtitles(self):
        text = (
            "SUMMIT SURFACE RENEWAL\n"
            "Residential turnover proposal | Riverside County\n"
            "PROPOSAL\n"
            "SSR-2217"
        )
        self.assertEqual(find_vendor_name(text), "SUMMIT SURFACE RENEWAL")

    def test_returns_none_when_vendor_heading_is_missing(self):
        self.assertIsNone(find_vendor_name("No recognizable document heading"))

    def test_finds_vendor_in_both_sample_estimates(self):
        blue_oak = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        )
        inland_pro = extract_pdf_text(
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf"
        )
        self.assertEqual(find_vendor_name(blue_oak), "Blue Oak Painting Co.")
        self.assertEqual(find_vendor_name(inland_pro), "Inland Pro Paint & Repair")

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
