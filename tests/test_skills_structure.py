import re
import unittest

from helpers import REPO

SKILLS = REPO / "plugins/arabic-gov-skills/skills"
EXPECTED = {"arabic-design-workflow", "arabic-rtl-docs", "formal-memo-ar", "formal-writing-ar",
            "document-pattern-analysis"}


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M)) if m else {}


class SkillStructureTests(unittest.TestCase):
    def test_expected_skills_present(self):
        self.assertEqual({p.name for p in SKILLS.iterdir() if p.is_dir()}, EXPECTED)

    def test_frontmatter_name_matches_folder_and_has_description(self):
        for d in SKILLS.iterdir():
            fm = frontmatter(d / "SKILL.md")
            self.assertEqual(fm.get("name"), d.name, d.name)
            self.assertGreater(len(fm.get("description", "")), 80, d.name)

    def test_readme_lists_every_skill(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        for name in EXPECTED:
            self.assertIn("`" + name + "`", readme, name)

    def test_adapted_third_party_content_is_attributed(self):
        floor = SKILLS / "arabic-design-workflow/references/design-floor.md"
        self.assertTrue(floor.exists())
        self.assertIn("pbakaus/impeccable", floor.read_text(encoding="utf-8"))
        notices = (REPO / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("Apache License", notices)
        self.assertIn("pbakaus/impeccable", notices)


if __name__ == "__main__":
    unittest.main()
