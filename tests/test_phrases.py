import unittest

from helpers import SCRIPT, clean_path, make_office, read_part, run_cli, tmpdir

PHRASES_FILE = SCRIPT.parent / "ai_phrases_ar.txt"


def ar(*cps):
    return "".join(chr(c) for c in cps)


# "tajdur al-ishara ila" (it is worth noting), written with code points
WORTH_NOTING = ar(0x062A, 0x062C, 0x062F, 0x0631, 0x0020, 0x0627, 0x0644, 0x0625, 0x0634, 0x0627, 0x0631, 0x0629)
# "yal'ab dawran mihwariyyan" with tanween fath on both words
PIVOTAL_ROLE = ar(0x064A, 0x0644, 0x0639, 0x0628, 0x0020, 0x062F, 0x0648, 0x0631, 0x064B, 0x0627, 0x0020,
                  0x0645, 0x062D, 0x0648, 0x0631, 0x064A, 0x064B, 0x0627)
WORD = ar(0x062A, 0x0642, 0x0631, 0x064A, 0x0631)
CT = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'


class PhraseTests(unittest.TestCase):
    def test_stock_phrase_reported_without_blocking(self):
        with tmpdir() as d:
            f = d / "a.txt"
            f.write_text(WORTH_NOTING + " " + WORD, encoding="utf-8")
            r = run_cli(f)
            self.assertIn("AI-STYLE PHRASE", r.stdout)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_phrase_matched_through_diacritics(self):
        with tmpdir() as d:
            f = d / "a.txt"
            f.write_text(WORD + " " + PIVOTAL_ROLE, encoding="utf-8")
            r = run_cli(f)
            self.assertIn("AI-STYLE PHRASE", r.stdout)

    def test_fix_leaves_phrase_text_unchanged(self):
        with tmpdir() as d:
            f = d / "a.txt"
            src = WORTH_NOTING + " " + WORD
            f.write_text(src, encoding="utf-8")
            run_cli(f, "--fix")
            self.assertEqual(clean_path(f).read_text(encoding="utf-8"), src)

    def test_phrase_reported_in_docx_text(self):
        with tmpdir() as d:
            f = make_office(d / "a.docx", {"[Content_Types].xml": CT,
                                           "word/document.xml": "<w:p><w:r><w:t>" + WORTH_NOTING + "</w:t></w:r></w:p>"})
            r = run_cli(f)
            self.assertIn("AI-STYLE PHRASE", r.stdout)

    def test_plain_text_without_phrases_not_flagged(self):
        with tmpdir() as d:
            f = d / "a.txt"
            f.write_text(WORD + " " + WORD, encoding="utf-8")
            r = run_cli(f)
            self.assertNotIn("AI-STYLE PHRASE", r.stdout)

    def test_phrase_list_file_has_no_hidden_characters(self):
        with tmpdir() as d:
            f = d / "list.md"
            f.write_bytes(PHRASES_FILE.read_bytes())
            r = run_cli(f)
            self.assertNotIn("U+", r.stdout)
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
