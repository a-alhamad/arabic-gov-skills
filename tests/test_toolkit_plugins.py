import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from helpers import REPO

GATEWAY = REPO / "plugins/free-llm-gateway/skills/free-llm-gateway/scripts/gateway.py"
TEMPLATES = REPO / "plugins/gov-templates/skills/presentation-templates"
KEYS = ["GEMINI_API_KEY", "GROQ_API_KEY", "CEREBRAS_API_KEY", "MISTRAL_API_KEY",
        "OPENROUTER_API_KEY"]


def load_gateway():
    spec = importlib.util.spec_from_file_location("gateway", GATEWAY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clean_env(**keys):
    env = {k: v for k, v in os.environ.items() if k not in KEYS and not k.startswith("FREE_GW_")}
    env.update(keys)
    return env


class GatewayConfigTests(unittest.TestCase):
    def config(self, **keys):
        with mock.patch.dict(os.environ, clean_env(**keys), clear=True):
            gw = load_gateway()
            return gw.build_config(gw.available())

    def test_no_key_refuses_with_list_of_variables(self):
        with self.assertRaises(SystemExit) as cm:
            self.config()
        self.assertIn("GEMINI_API_KEY", str(cm.exception))

    def test_only_providers_with_keys_are_included(self):
        cfg = self.config(GROQ_API_KEY="x", MISTRAL_API_KEY="y")
        names = [m["model_name"] for m in cfg["model_list"]]
        self.assertEqual(names, ["groq", "mistral", "free"])

    def test_free_alias_uses_first_provider_and_falls_back_to_rest_in_order(self):
        cfg = self.config(GEMINI_API_KEY="a", CEREBRAS_API_KEY="b", OPENROUTER_API_KEY="c")
        free = [m for m in cfg["model_list"] if m["model_name"] == "free"][0]
        self.assertTrue(free["litellm_params"]["model"].startswith("gemini/"))
        self.assertEqual(cfg["router_settings"]["fallbacks"], [{"free": ["cerebras", "openrouter"]}])

    def test_keys_are_referenced_never_embedded(self):
        cfg = self.config(GEMINI_API_KEY="secret-value-123")
        text = json.dumps(cfg)
        self.assertNotIn("secret-value-123", text)
        self.assertIn("os.environ/GEMINI_API_KEY", text)

    def test_model_override_from_environment(self):
        cfg = self.config(GEMINI_API_KEY="a", FREE_GW_GEMINI_MODEL="gemini/other")
        self.assertEqual(cfg["model_list"][0]["litellm_params"]["model"], "gemini/other")

    def test_cli_providers_runs_without_keys(self):
        out = subprocess.run([sys.executable, "-I", str(GATEWAY), "providers"],
                             capture_output=True, text=True, env=clean_env())
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.count("missing"), len(KEYS))


class TemplateTests(unittest.TestCase):
    def test_every_template_is_a_valid_pptx_and_documented(self):
        skill = (TEMPLATES / "SKILL.md").read_text(encoding="utf-8")
        files = sorted((TEMPLATES / "assets").glob("*.pptx"))
        self.assertTrue(files)
        for f in files:
            with zipfile.ZipFile(f) as z:
                self.assertIn("ppt/presentation.xml", z.namelist(), f.name)
            self.assertIn(f"assets/{f.name}", skill, f.name)

    def test_template_names_are_shell_safe(self):
        for f in (TEMPLATES / "assets").iterdir():
            self.assertRegex(f.name, r"^[a-z0-9-]+\.pptx$")


class SkillFrontmatterTests(unittest.TestCase):
    def test_new_skills_have_matching_name_and_description(self):
        for skill in [GATEWAY.parent.parent, TEMPLATES]:
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            fm = dict(re.findall(r"^(\w+):\s*(.+)$", text.split("---")[1], re.M))
            self.assertEqual(fm.get("name"), skill.name)
            self.assertGreater(len(fm.get("description", "")), 80)


if __name__ == "__main__":
    unittest.main()
