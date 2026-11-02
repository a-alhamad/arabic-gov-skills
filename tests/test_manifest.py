import json
import re
import unittest

from helpers import REPO

MARKET = REPO / ".claude-plugin/marketplace.json"


def market():
    return json.loads(MARKET.read_text(encoding="utf-8"))


def plugin_manifest(entry):
    path = REPO / entry["source"] / ".claude-plugin/plugin.json"
    return json.loads(path.read_text(encoding="utf-8"))


class ManifestTests(unittest.TestCase):
    def test_every_plugin_declares_semver_version(self):
        for entry in market()["plugins"]:
            self.assertRegex(plugin_manifest(entry).get("version", ""), r"^\d+\.\d+\.\d+$",
                             entry["name"])

    def test_marketplace_entries_do_not_duplicate_version(self):
        for entry in market()["plugins"]:
            self.assertNotIn("version", entry, entry["name"])

    def test_marketplace_entries_match_plugin_manifests(self):
        for entry in market()["plugins"]:
            plugin = plugin_manifest(entry)
            self.assertEqual(entry["name"], plugin["name"])
            self.assertEqual(entry["description"], plugin["description"], entry["name"])
        self.assertIn("design", market()["description"])

    def test_every_plugin_folder_is_listed(self):
        listed = {e["source"].removeprefix("./") for e in market()["plugins"]}
        on_disk = {f"plugins/{p.name}" for p in (REPO / "plugins").iterdir() if p.is_dir()}
        self.assertEqual(listed, on_disk)

    def test_readme_lists_every_plugin(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        for entry in market()["plugins"]:
            self.assertIn("`" + entry["name"] + "`", readme, entry["name"])


if __name__ == "__main__":
    unittest.main()
