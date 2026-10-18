import json
import re
import unittest

from helpers import REPO

PLUGIN = REPO / "plugins/arabic-gov-skills/.claude-plugin/plugin.json"
MARKET = REPO / ".claude-plugin/marketplace.json"


class ManifestTests(unittest.TestCase):
    def test_plugin_declares_semver_version(self):
        version = json.loads(PLUGIN.read_text(encoding="utf-8")).get("version", "")
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")

    def test_marketplace_entry_does_not_duplicate_version(self):
        entry = json.loads(MARKET.read_text(encoding="utf-8"))["plugins"][0]
        self.assertNotIn("version", entry)

    def test_marketplace_and_plugin_descriptions_match(self):
        market = json.loads(MARKET.read_text(encoding="utf-8"))
        plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
        self.assertEqual(market["plugins"][0]["description"], plugin["description"])
        self.assertIn("design", market["description"])


if __name__ == "__main__":
    unittest.main()
