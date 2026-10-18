#!/usr/bin/env python3
"""Detect (and optionally remove) hidden Unicode characters in Arabic documents.

Supports: .docx, .pptx, .xlsx (XML parts inside the archive), and plain-text
formats (.html, .htm, .md, .txt, .xml).

Usage:
    check_hidden_chars.py FILE          # report only
    check_hidden_chars.py FILE --fix    # write FILE_clean.<ext>, original untouched
"""
import sys
import zipfile
from collections import Counter
from pathlib import Path

REMOVE = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200d": "ZERO WIDTH JOINER",
    "\u200e": "LEFT-TO-RIGHT MARK",
    "\u200f": "RIGHT-TO-LEFT MARK",
    "\u202a": "LEFT-TO-RIGHT EMBEDDING",
    "\u202b": "RIGHT-TO-LEFT EMBEDDING",
    "\u202c": "POP DIRECTIONAL FORMATTING",
    "\u202d": "LEFT-TO-RIGHT OVERRIDE",
    "\u202e": "RIGHT-TO-LEFT OVERRIDE",
    "\u2066": "LEFT-TO-RIGHT ISOLATE",
    "\u2067": "RIGHT-TO-LEFT ISOLATE",
    "\u2068": "FIRST STRONG ISOLATE",
    "\u2069": "POP DIRECTIONAL ISOLATE",
    "\ufeff": "BYTE ORDER MARK",
}
REPLACE = {
    "\u00a0": (" ", "NO-BREAK SPACE"),
    "\u201c": ('"', "LEFT DOUBLE QUOTE"),
    "\u201d": ('"', "RIGHT DOUBLE QUOTE"),
    "\u2018": ("'", "LEFT SINGLE QUOTE"),
    "\u2019": ("'", "RIGHT SINGLE QUOTE"),
}
REPORT_ONLY = {"\u200c": "ZERO WIDTH NON-JOINER (review manually)"}

ZIP_EXT = {".docx", ".pptx", ".xlsx"}
TEXT_EXT = {".html", ".htm", ".md", ".txt", ".xml"}


def scan(text: str) -> Counter:
    found = Counter()
    for ch in text:
        if ch in REMOVE or ch in REPLACE or ch in REPORT_ONLY:
            found[ch] += 1
    return found


def clean(text: str) -> str:
    for ch in REMOVE:
        text = text.replace(ch, "")
    for ch, (rep, _) in REPLACE.items():
        text = text.replace(ch, rep)
    return text


def label(ch: str) -> str:
    if ch in REMOVE:
        return f"U+{ord(ch):04X} {REMOVE[ch]} -> remove"
    if ch in REPLACE:
        return f"U+{ord(ch):04X} {REPLACE[ch][1]} -> replace"
    return f"U+{ord(ch):04X} {REPORT_ONLY[ch]}"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    fix = "--fix" in sys.argv[2:]
    ext = path.suffix.lower()
    total = Counter()

    if ext in ZIP_EXT:
        with zipfile.ZipFile(path) as zin:
            parts = {n: zin.read(n) for n in zin.namelist()}
        out_parts = {}
        for name, data in parts.items():
            if name.endswith((".xml", ".rels")):
                text = data.decode("utf-8")
                total += scan(text)
                out_parts[name] = clean(text).encode("utf-8") if fix else data
            else:
                out_parts[name] = data
        if fix:
            out = path.with_name(f"{path.stem}_clean{path.suffix}")
            with zipfile.ZipFile(path) as zin, zipfile.ZipFile(out, "w") as zout:
                for info in zin.infolist():
                    zout.writestr(info, out_parts[info.filename], zipfile.ZIP_DEFLATED)
    elif ext in TEXT_EXT:
        text = path.read_text(encoding="utf-8")
        total = scan(text)
        if fix:
            out = path.with_name(f"{path.stem}_clean{path.suffix}")
            out.write_text(clean(text), encoding="utf-8")
    else:
        print(f"Unsupported file type: {ext}")
        return 2

    if not total:
        print("Clean: no hidden or non-standard characters found.")
    else:
        for ch, n in sorted(total.items()):
            print(f"{n:>6}  {label(ch)}")
    if fix:
        print(f"Cleaned copy written: {out}")
    return 1 if total and not fix else 0


if __name__ == "__main__":
    sys.exit(main())
