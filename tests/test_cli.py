import unittest

from helpers import SCRIPT, clean_path, run_cli, tmpdir

ARABIC_OK = "".join(chr(c) for c in (0x0646, 0x0635, 0x0020, 0x0633, 0x0644, 0x064A, 0x0645)) + " ISSAI 100."


class CliTests(unittest.TestCase):
    def test_script_source_is_ascii_only(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertEqual(sum(1 for c in text if ord(c) > 127), 0)

    def test_clean_text_exits_zero(self):
        with tmpdir() as d:
            f = d / "ok.txt"
            f.write_text(ARABIC_OK, encoding="utf-8")
            r = run_cli(f)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(r.stdout.startswith("Clean"))

    def test_unsupported_extension_exits_two(self):
        with tmpdir() as d:
            f = d / "old.doc"
            f.write_bytes(b"binary")
            self.assertEqual(run_cli(f).returncode, 2)

    def test_fix_never_modifies_original(self):
        with tmpdir() as d:
            f = d / "a.txt"
            f.write_text(ARABIC_OK + chr(0x200F) + "**x**", encoding="utf-8")
            before = f.read_bytes()
            r = run_cli(f, "--fix")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(f.read_bytes(), before)
            self.assertTrue(clean_path(f).exists())


if __name__ == "__main__":
    unittest.main()
