import unittest

from helpers import clean_path, run_cli, tmpdir

WORD = "".join(chr(c) for c in (0x062A, 0x0642, 0x0631, 0x064A, 0x0631))
TITLE = "".join(chr(c) for c in (0x0639, 0x0646, 0x0648, 0x0627, 0x0646))
NOTE = "".join(chr(c) for c in (0x0627, 0x0644, 0x062D, 0x0627, 0x0634, 0x064A, 0x0629))


def fix(text, name="in.txt"):
    with tmpdir() as d:
        f = d / name
        f.write_text(text, encoding="utf-8")
        r = run_cli(f, "--fix")
        return r, clean_path(f).read_text(encoding="utf-8")


class TextLayerTests(unittest.TestCase):
    def test_em_dash_reported_not_removed(self):
        r, out = fix(WORD + " " + chr(0x2014) + " " + WORD)
        self.assertIn(chr(0x2014), out)
        self.assertIn("EM DASH", r.stdout)

    def test_presentation_form_normalized(self):
        _, out = fix(chr(0xFEFB))
        self.assertEqual(out, chr(0x0644) + chr(0x0627))

    def test_farsi_yeh_reported_not_changed(self):
        r, out = fix(WORD + chr(0x06CC))
        self.assertIn(chr(0x06CC), out)
        self.assertIn("FARSI YEH", r.stdout)

    def test_mixed_script_word_reported(self):
        token = "ISS" + chr(0x0410) + "I"
        r, _ = fix(WORD + " " + token)
        self.assertIn(repr(token), r.stdout)

    def test_txt_markdown_stripped(self):
        src = "## " + TITLE + "\n- " + WORD + "\n**" + WORD + "**\n---\n" + WORD + "\n"
        _, out = fix(src)
        self.assertNotIn("#", out)
        self.assertNotIn("**", out)
        self.assertNotIn("- ", out)
        self.assertNotIn("---", out)
        self.assertEqual(out, TITLE + "\n" + WORD + "\n" + WORD + "\n" + WORD + "\n")

    def test_single_asterisk_kept(self):
        src = NOTE + "* " + WORD
        _, out = fix(src)
        self.assertEqual(out, src)

    def test_md_file_markdown_untouched(self):
        src = "## " + TITLE + "\n- " + WORD + "\n**" + WORD + "**\n"
        _, out = fix(src, name="doc.md")
        self.assertEqual(out, src)


if __name__ == "__main__":
    unittest.main()
