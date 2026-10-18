import unittest

from helpers import clean_path, make_office, read_part, run_cli, tmpdir

WORD = "".join(chr(c) for c in (0x0645, 0x0644, 0x062E, 0x0635))
AUTHOR = "".join(chr(c) for c in (0x0622, 0x0644, 0x0627, 0x0621))
CT = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'


def doc_xml(text):
    return '<w:document><w:body><w:p><w:r><w:t>' + text + '</w:t></w:r></w:p></w:body></w:document>'


def core_xml(creator):
    return ('<cp:coreProperties xmlns:dc="http://purl.org/dc/elements/1.1/">'
            '<dc:creator>' + creator + '</dc:creator></cp:coreProperties>')


class OfficeHtmlTests(unittest.TestCase):
    def test_docx_bold_markers_removed_from_document(self):
        with tmpdir() as d:
            f = make_office(d / "a.docx", {"[Content_Types].xml": CT, "word/document.xml": doc_xml("**" + WORD + "**")})
            run_cli(f, "--fix")
            self.assertIn("<w:t>" + WORD + "</w:t>", read_part(clean_path(f), "word/document.xml"))

    def test_docx_font_names_untouched(self):
        font = '<w:fonts><w:font w:name="' + chr(0xFF2D) + chr(0xFF33) + '"/></w:fonts>'
        with tmpdir() as d:
            f = make_office(d / "a.docx", {"[Content_Types].xml": CT, "word/document.xml": doc_xml(WORD),
                                           "word/fontTable.xml": font})
            r = run_cli(f, "--fix")
            self.assertEqual(read_part(clean_path(f), "word/fontTable.xml"), font)
            self.assertNotIn("FF2D", r.stdout)

    def test_generator_creator_cleared(self):
        with tmpdir() as d:
            f = make_office(d / "a.docx", {"[Content_Types].xml": CT, "word/document.xml": doc_xml(WORD),
                                           "docProps/core.xml": core_xml("python-docx")})
            run_cli(f, "--fix")
            self.assertIn("<dc:creator></dc:creator>", read_part(clean_path(f), "docProps/core.xml"))

    def test_real_author_preserved(self):
        with tmpdir() as d:
            f = make_office(d / "a.docx", {"[Content_Types].xml": CT, "word/document.xml": doc_xml(WORD),
                                           "docProps/core.xml": core_xml(AUTHOR)})
            run_cli(f, "--fix")
            self.assertIn("<dc:creator>" + AUTHOR + "</dc:creator>", read_part(clean_path(f), "docProps/core.xml"))

    def test_docx_without_docprops_works(self):
        with tmpdir() as d:
            f = make_office(d / "a.docx", {"[Content_Types].xml": CT, "word/document.xml": doc_xml(WORD)})
            r = run_cli(f)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_html_generator_meta_removed(self):
        with tmpdir() as d:
            f = d / "p.html"
            f.write_text('<html dir="rtl"><head><meta name="generator" content="X"></head><body>' + WORD + '</body></html>',
                         encoding="utf-8")
            run_cli(f, "--fix")
            self.assertNotIn("generator", clean_path(f).read_text(encoding="utf-8"))

    def test_md_mentioning_meta_not_flagged(self):
        with tmpdir() as d:
            f = d / "doc.md"
            f.write_text(WORD + ' `<meta name="generator">` ' + WORD, encoding="utf-8")
            r = run_cli(f)
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
