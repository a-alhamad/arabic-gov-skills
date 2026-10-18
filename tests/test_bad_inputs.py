import struct
import unittest

from helpers import clean_path, make_office, run_cli, tmpdir

WORD = "".join(chr(c) for c in (0x062A, 0x0642, 0x0631, 0x064A, 0x0631))
NAME = "".join(chr(c) for c in (0x062A, 0x0642, 0x0631, 0x064A, 0x0631)) + " " + "".join(
    chr(c) for c in (0x0627, 0x0644, 0x0631, 0x0642, 0x0627, 0x0628, 0x0629))


class BadInputTests(unittest.TestCase):
    def test_non_utf8_text_exits_two_with_message(self):
        with tmpdir() as d:
            f = d / "legacy.txt"
            f.write_bytes(WORD.encode("cp1256"))
            r = run_cli(f)
            self.assertEqual(r.returncode, 2)
            self.assertIn("UTF-8", r.stdout)
            self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_missing_file_exits_two_with_message(self):
        with tmpdir() as d:
            r = run_cli(d / "absent.docx")
            self.assertEqual(r.returncode, 2)
            self.assertIn("not found", r.stdout)
            self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_corrupt_docx_exits_two_with_message(self):
        with tmpdir() as d:
            f = d / "broken.docx"
            f.write_text("plain text, not a zip", encoding="utf-8")
            r = run_cli(f)
            self.assertEqual(r.returncode, 2)
            self.assertIn("not a valid", r.stdout)
            self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_arabic_filename_with_spaces(self):
        with tmpdir() as d:
            f = d / (NAME + ".txt")
            f.write_text(WORD + chr(0x200B), encoding="utf-8")
            r = run_cli(f, "--fix")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue((d / (NAME + "_clean.txt")).exists())
            self.assertEqual(clean_path(f).read_text(encoding="utf-8"), WORD)

    def test_damaged_zip_member_exits_two_with_message(self):
        with tmpdir() as d:
            f = make_office(d / "damaged.docx", {"word/document.xml": "<w:t>" + WORD * 400 + "</w:t>"})
            raw = bytearray(f.read_bytes())
            header = 30 + len("word/document.xml")
            for i in range(header, header + 4):
                raw[i] = 0xFF  # invalid deflate block type: zlib.error on read
            f.write_bytes(bytes(raw))
            r = run_cli(f)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("not a valid", r.stdout)
            self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_encrypted_zip_member_exits_two_with_message(self):
        with tmpdir() as d:
            f = make_office(d / "locked.docx", {"word/document.xml": "<w:t>" + WORD + "</w:t>"})
            raw = bytearray(f.read_bytes())
            cd = raw.find(b"PK\x01\x02")
            flags = struct.unpack_from("<H", raw, cd + 8)[0]
            struct.pack_into("<H", raw, cd + 8, flags | 0x1)
            f.write_bytes(bytes(raw))
            r = run_cli(f)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("not a valid", r.stdout)
            self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_fix_flag_before_path_works(self):
        with tmpdir() as d:
            f = d / "a.txt"
            f.write_text(WORD + chr(0x200B), encoding="utf-8")
            r = run_cli("--fix", str(f))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(clean_path(f).read_text(encoding="utf-8"), WORD)


if __name__ == "__main__":
    unittest.main()
