import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app
from app.ai_extractor import AIExtractionBatch


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"
CLIENT = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_health_check(self):
        response = CLIENT.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("ai_enabled", response.json())
        self.assertEqual(
            response.json()["supported_trades"],
            [
                {"key": "painting", "label": "Interior painting"},
                {"key": "flooring", "label": "Flooring"},
                {"key": "plumbing", "label": "Plumbing"},
                {"key": "hvac", "label": "HVAC"},
            ],
        )

    def test_normalizes_uploaded_estimate(self):
        path = QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        with path.open("rb") as pdf:
            response = CLIENT.post(
                "/estimates/normalize",
                files={"estimate": (path.name, pdf, "application/pdf")},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["vendor_name"], "Blue Oak Painting Co.")
        self.assertEqual(response.json()["estimate_total"], "$4,750.00")

    def test_compares_two_uploaded_estimates(self):
        first = QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        second = QUOTES / "synthetic-painting-estimate-inland-pro.pdf"
        with first.open("rb") as first_pdf, second.open("rb") as second_pdf:
            response = CLIENT.post(
                "/estimates/compare",
                files={
                    "first_estimate": (first.name, first_pdf, "application/pdf"),
                    "second_estimate": (second.name, second_pdf, "application/pdf"),
                },
            )
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["price_difference_cents"], 86000)
        self.assertEqual(result["lower_bidder"], "Inland Pro Paint & Repair")
        self.assertEqual(len(result["risk_flags"]), 7)

    def test_compares_three_uploaded_estimates(self):
        paths = [
            QUOTES / "synthetic-painting-estimate-blue-oak.pdf",
            QUOTES / "synthetic-painting-estimate-inland-pro.pdf",
            QUOTES / "synthetic-painting-proposal-canyon-view.pdf",
        ]
        opened = [path.open("rb") for path in paths]
        try:
            response = CLIENT.post(
                "/estimates/compare-many",
                files=[
                    ("estimates", (path.name, pdf, "application/pdf"))
                    for path, pdf in zip(paths, opened)
                ],
            )
        finally:
            for pdf in opened:
                pdf.close()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["vendors"]), 3)
        self.assertIn("price_range_cents", response.json())

    def test_multi_comparison_requires_at_least_two_estimates(self):
        path = QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        with path.open("rb") as pdf:
            response = CLIENT.post(
                "/estimates/compare-many",
                files={"estimates": (path.name, pdf, "application/pdf")},
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("between 2 and 5", response.json()["detail"])

    def test_rejects_unsupported_upload(self):
        response = CLIENT.post(
            "/estimates/normalize",
            files={"estimate": ("quote.txt", b"not a PDF", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Supported files are PDF", response.json()["detail"])

    def test_rejects_file_with_mismatched_extension(self):
        response = CLIENT.post(
            "/estimates/normalize",
            files={"estimate": ("quote.jpg", b"not an image", "image/jpeg")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("do not match", response.json()["detail"])

    def test_image_requires_configured_ocr(self):
        with patch("app.api.configured_ai_extractor", return_value=None):
            response = CLIENT.post(
                "/estimates/normalize",
                files={
                    "estimate": (
                        "quote.png",
                        b"\x89PNG\r\n\x1a\nplaceholder",
                        "image/png",
                    )
                },
            )
        self.assertEqual(response.status_code, 422)
        self.assertIn("require AI OCR", response.json()["detail"])

    def test_normalizes_image_with_configured_ocr(self):
        class FakeImageExtractor:
            def transcribe_image(self, image_path):
                self.suffix = image_path.suffix
                return (
                    "Pixel Plumbing Co.\nESTIMATE\n"
                    "Water heater included\nESTIMATE TOTAL $3,250.00"
                )

            def classify(self, estimate_text, categories):
                return AIExtractionBatch(classifications=[])

        extractor = FakeImageExtractor()
        with patch("app.api.configured_ai_extractor", return_value=extractor):
            response = CLIENT.post(
                "/estimates/normalize",
                data={"trade": "plumbing"},
                files={
                    "estimate": (
                        "quote.jpg",
                        b"\xff\xd8\xffplaceholder",
                        "image/jpeg",
                    )
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["vendor_name"], "Pixel Plumbing Co.")
        self.assertEqual(response.json()["estimate_total"], "$3,250.00")
        self.assertEqual(extractor.suffix, ".jpg")

    def test_rejects_unsupported_trade(self):
        path = QUOTES / "synthetic-painting-estimate-blue-oak.pdf"
        with path.open("rb") as pdf:
            response = CLIENT.post(
                "/estimates/normalize",
                data={"trade": "roofing"},
                files={"estimate": (path.name, pdf, "application/pdf")},
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported trade 'roofing'", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
