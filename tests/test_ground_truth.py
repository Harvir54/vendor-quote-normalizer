import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GROUND_TRUTH = ROOT / "sample-data" / "ground-truth"
VALID_STATUSES = {"included", "excluded", "not_stated", "unclear"}
REQUIRED_CATEGORIES = {
    "surface_protection",
    "drywall_repair",
    "primer",
    "walls",
    "wall_coat_count",
    "ceilings",
    "trim",
    "interior_doors",
    "paint_and_materials",
    "cleanup",
    "debris_disposal",
    "labor_warranty",
}


class GroundTruthTests(unittest.TestCase):
    def setUp(self):
        self.records = [json.loads(path.read_text()) for path in sorted(GROUND_TRUTH.glob("*.json"))]

    def test_two_fixtures_exist(self):
        self.assertEqual(len(self.records), 2)

    def test_source_pdfs_exist(self):
        for record in self.records:
            source = (GROUND_TRUTH / record["document"]["source_file"]).resolve()
            self.assertTrue(source.is_file(), source)

    def test_required_categories_and_statuses(self):
        for record in self.records:
            items = record["scope_items"]
            self.assertEqual({item["category"] for item in items}, REQUIRED_CATEGORIES)
            self.assertTrue(all(item["status"] in VALID_STATUSES for item in items))

    def test_line_items_match_total(self):
        for record in self.records:
            line_total = sum(item["amount_cents"] for item in record["line_items"])
            self.assertEqual(line_total, record["estimate"]["total_cents"])

    def test_fixture_ids_are_unique(self):
        ids = [record["document"]["fixture_id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
