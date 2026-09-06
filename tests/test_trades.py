import unittest

from app.trades import (
    UnsupportedTradeError,
    get_trade_profile,
    supported_trades,
)


class TradeProfileTests(unittest.TestCase):
    def test_painting_profile_defines_scope_and_risk_fields(self):
        profile = get_trade_profile("painting")
        self.assertEqual(profile.label, "Interior painting")
        self.assertEqual(set(profile.scope_labels), set(profile.classifiers))
        self.assertIn("walls", profile.scope_labels)
        self.assertIn("labor_warranty", profile.risk_descriptions)

    def test_lists_supported_trade_metadata(self):
        self.assertEqual(
            supported_trades(),
            [
                {"key": "painting", "label": "Interior painting"},
                {"key": "flooring", "label": "Flooring"},
            ],
        )

    def test_rejects_unknown_trade(self):
        with self.assertRaises(UnsupportedTradeError):
            get_trade_profile("plumbing")


if __name__ == "__main__":
    unittest.main()
