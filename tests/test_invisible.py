import unittest

from helpers import clean_path, run_cli, tmpdir

WORD = "".join(chr(c) for c in (0x062A, 0x0642, 0x0631, 0x064A, 0x0631))  # Arabic word


def fix_text(text):
    with tmpdir() as d:
        f = d / "in.txt"
        f.write_text(text, encoding="utf-8")
        r = run_cli(f, "--fix")
        return r, clean_path(f).read_text(encoding="utf-8")


class InvisibleTests(unittest.TestCase):
    def test_removes_zero_width_and_directional(self):
        bad = [0x200B, 0x200F, 0x202E, 0x2066, 0xFEFF]
        _, out = fix_text(WORD + "".join(chr(c) for c in bad) + WORD)
        for c in bad:
            self.assertNotIn(chr(c), out, f"U+{c:04X} survived")
        self.assertEqual(out, WORD + WORD)

    def test_removes_tag_characters(self):
        _, out = fix_text(WORD + chr(0xE0041) + chr(0xE007F))
        self.assertEqual(out, WORD)

    def test_replaces_nbsp_and_curly_quotes(self):
        _, out = fix_text(chr(0x201C) + WORD + chr(0x201D) + chr(0x00A0) + WORD)
        self.assertEqual(out, '"' + WORD + '" ' + WORD)

    def test_keeps_zwnj_and_reports_it(self):
        r, out = fix_text(WORD + chr(0x200C) + WORD)
        self.assertIn(chr(0x200C), out)
        self.assertIn("U+200C", r.stdout)

    def test_report_mode_exits_one_on_invisible(self):
        with tmpdir() as d:
            f = d / "in.txt"
            f.write_text(WORD + chr(0x200B), encoding="utf-8")
            self.assertEqual(run_cli(f).returncode, 1)


if __name__ == "__main__":
    unittest.main()
