"""Shared helpers for the checker test suite. Standard library only."""
import contextlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "plugins/arabic-gov-skills/skills/arabic-rtl-docs/scripts/check_hidden_chars.py"


def run_cli(path, *args, script=None):
    """Run the checker as a user would. Returns CompletedProcess with text output."""
    cmd = [sys.executable, "-I", str(script or SCRIPT), str(path), *args]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def make_office(path, parts):
    """Write a zip archive whose members are the given {name: xml_text} parts."""
    path = Path(path)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts.items():
            z.writestr(name, text.encode("utf-8"))
    return path


def read_part(path, name):
    with zipfile.ZipFile(path) as z:
        return z.read(name).decode("utf-8")


def clean_path(path):
    path = Path(path)
    return path.with_name(f"{path.stem}_clean{path.suffix}")


@contextlib.contextmanager
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)
