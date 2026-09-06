import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.api import app


ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / "sample-data" / "quotes"
CLIENT = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_health_check(self):
        response = CLIENT.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("ai_enabled", response.json())

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
        self.assertEqual(len(result["risk_flags"]), 6)

    def test_rejects_non_pdf_upload(self):
        response = CLIENT.post(
            "/estimates/normalize",
            files={"estimate": ("quote.txt", b"not a PDF", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Only PDF files are supported.")


if __name__ == "__main__":
    unittest.main()
