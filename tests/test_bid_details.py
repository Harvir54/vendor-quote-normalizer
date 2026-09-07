import unittest

from app.bid_details import extract_bid_details


class BidDetailsTests(unittest.TestCase):
    def test_extracts_common_contract_fields(self):
        text = """Blue Oak Painting Co.
ESTIMATE
CA Lic. #SYN-1047281
Estimate #: BOP-260814
Issued: August 14, 2026
Valid through: September 13, 2026
Work is expected to require four working days after access is provided.
EXCLUSIONS
Cabinets and closets; moving tenant belongings.
TERMS AND ACCEPTANCE
A 40% deposit is due upon scheduling. The balance is due after walkthrough.
"""

        details = extract_bid_details(text)

        self.assertEqual(details["proposal_number"], "BOP-260814")
        self.assertEqual(details["issued_date"], "August 14, 2026")
        self.assertEqual(details["valid_until"], "September 13, 2026")
        self.assertEqual(details["contractor_license"], "SYN-1047281")
        self.assertIn("four working days", details["project_schedule"])
        self.assertIn("40% deposit", details["payment_terms"])
        self.assertIn("Cabinets and closets", details["exclusions"])

    def test_keeps_unstated_fields_empty(self):
        details = extract_bid_details("ACME FLOORING\nESTIMATE TOTAL $2,000.00")

        self.assertTrue(all(value is None for value in details.values()))

    def test_extracts_inline_estimate_and_validity(self):
        details = extract_bid_details(
            "Estimate PF-2048 | Residential flooring\nValid for 30 days"
        )

        self.assertEqual(details["proposal_number"], "PF-2048")
        self.assertEqual(details["valid_until"], "Valid for 30 days")

    def test_does_not_treat_next_table_cell_as_validity_date(self):
        details = extract_bid_details(
            "PROJECT\nDATE\nVALID THROUGH\nRiverside\nResidential Partners"
        )

        self.assertIsNone(details["valid_until"])
