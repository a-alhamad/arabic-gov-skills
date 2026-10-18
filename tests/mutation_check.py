"""Prove the test suite can fail: break one behavior at a time in a temporary
copy of the checker and require at least one test to fail for each break.

Run from the repository root:  python3 tests/mutation_check.py
Exit code 0 only if every mutation is detected.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REL = "plugins/arabic-gov-skills/skills/arabic-rtl-docs/scripts/check_hidden_chars.py"

MUTATIONS = [
    ("drop U+200B from REMOVE", '    0x200B: "ZERO WIDTH SPACE",\n', ""),
    ("drop tag-character range", '    (0xE0000, 0xE007F, "TAG CHARACTER"),\n', ""),
    ("delete ZWNJ instead of keeping it",
     'if c is None or c[0] in ("review", "visible", "lookalike"):',
     'if c is None or c[0] in ("visible", "lookalike"):'),
    ("auto-remove em dash", '    0x2014: "EM DASH",\n', ""),
    ("skip NFKC normalization",
     'out.append(unicodedata.normalize("NFKC", ch))', "out.append(ch)"),
    ("normalize inside non-text parts",
     'elif c[0] == "normalize" and not text_part:', 'elif False:'),
    ("keep list markers in txt", "    text = MD_BULLET.sub(\"\", text)\n", ""),
    ("strip markdown in .md files", 'is_plain = ext == ".txt"', 'is_plain = ext in {".txt", ".md"}'),
    ("never clear generator metadata", "                    text = clean_meta(text)\n", ""),
    ("check generator meta in every text file", 'is_html = ext in {".html", ".htm"}', "is_html = True"),
    ("non-ASCII character in source", '"""Detect,', '"""' + chr(0x200F) + 'Detect,'),
    ("overwrite the original file", 'out = path.with_name(f"{path.stem}_clean{path.suffix}")', "out = path"),
    ("crash on non-UTF-8 input", "    except UnicodeDecodeError:\n", "    except KeyError:\n"),
]


def main():
    detected = 0
    for name, old, new in MUTATIONS:
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d) / "repo"
            shutil.copytree(REPO, copy, ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__"))
            target = copy / REL
            src = target.read_text(encoding="utf-8")
            if src.count(old) != 1:
                print(f"BROKEN MUTATION (pattern not found once): {name}")
                continue
            target.write_text(src.replace(old, new), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                               cwd=copy, capture_output=True, text=True)
            caught = r.returncode != 0
            detected += caught
            print(f"{'detected' if caught else 'MISSED  '}  {name}")
    print(f"{detected}/{len(MUTATIONS)} mutations detected")
    return 0 if detected == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())
