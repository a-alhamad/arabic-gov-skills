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
        "ZAI_API_KEY", "OPENROUTER_API_KEY", "MOONSHOT_API_KEY"]
STYLE_HOOK = GATEWAY.parent / "style_hook.py"


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
    def config(self, style=False, **keys):
        with mock.patch.dict(os.environ, clean_env(**keys), clear=True):
            gw = load_gateway()
            return gw.build_config(gw.available(), gw.available(gw.PAID_PROVIDERS), style=style)

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
        self.assertEqual(free["litellm_params"]["model"], "gemini/gemini-2.5-pro")
        self.assertEqual(cfg["router_settings"]["fallbacks"],
                         [{"free": ["gemini", "cerebras", "openrouter"]}])

    def test_one_gemini_key_gives_pro_then_flash(self):
        cfg = self.config(GEMINI_API_KEY="a")
        names = [m["model_name"] for m in cfg["model_list"]]
        self.assertEqual(names, ["gemini-pro", "gemini", "free"])
        self.assertEqual(cfg["router_settings"]["fallbacks"], [{"free": ["gemini"]}])

    def test_keys_are_referenced_never_embedded(self):
        cfg = self.config(GEMINI_API_KEY="secret-value-123")
        text = json.dumps(cfg)
        self.assertNotIn("secret-value-123", text)
        self.assertIn("os.environ/GEMINI_API_KEY", text)

    def test_model_override_from_environment(self):
        cfg = self.config(GEMINI_API_KEY="a", FREE_GW_GEMINI_MODEL="gemini/other",
                          FREE_GW_GEMINI_PRO_MODEL="gemini/pro-other")
        by_name = {m["model_name"]: m["litellm_params"]["model"] for m in cfg["model_list"]}
        self.assertEqual(by_name["gemini"], "gemini/other")
        self.assertEqual(by_name["gemini-pro"], "gemini/pro-other")

    def test_cli_providers_runs_without_keys(self):
        out = subprocess.run([sys.executable, "-I", str(GATEWAY), "providers"],
                             capture_output=True, text=True, env=clean_env())
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("free  gemini", out.stdout)
        self.assertIn("paid  kimi", out.stdout)

    def test_paid_models_are_callable_by_name_but_never_in_fallback(self):
        cfg = self.config(GEMINI_API_KEY="a", MOONSHOT_API_KEY="b", ZAI_API_KEY="c")
        names = [m["model_name"] for m in cfg["model_list"]]
        self.assertIn("kimi", names)
        self.assertIn("glm", names)
        chain = cfg["router_settings"]["fallbacks"][0]["free"]
        self.assertNotIn("kimi", chain)
        self.assertNotIn("glm", chain)
        self.assertIn("zai", chain)

    def test_paid_key_alone_does_not_start_gateway(self):
        with self.assertRaises(SystemExit):
            self.config(MOONSHOT_API_KEY="b")

    def test_zai_free_tier_uses_free_flash_model(self):
        cfg = self.config(ZAI_API_KEY="c")
        self.assertEqual(cfg["model_list"][0]["litellm_params"]["model"], "zai/glm-4.7-flash")

    def test_api_base_override(self):
        cfg = self.config(GROQ_API_KEY="a", FREE_GW_GROQ_API_BASE="http://x/v1")
        for m in cfg["model_list"]:
            self.assertEqual(m["litellm_params"]["api_base"], "http://x/v1")

    def test_style_hook_registered_only_when_style_found(self):
        self.assertNotIn("callbacks", self.config(GEMINI_API_KEY="a")["litellm_settings"])
        cfg = self.config(style=True, GEMINI_API_KEY="a")
        self.assertEqual(cfg["litellm_settings"]["callbacks"], "style_hook.proxy_handler_instance")

    def test_style_file_found_in_repo_layout(self):
        with mock.patch.dict(os.environ, clean_env(), clear=True):
            found = load_gateway().find_style_file()
        self.assertEqual(found, REPO / "plugins/arabic-gov-skills/skills/formal-writing-ar/SKILL.md")


def load_style_hook():
    spec = importlib.util.spec_from_file_location("style_hook", STYLE_HOOK)
    mod = importlib.util.module_from_spec(spec)
    with mock.patch.dict(os.environ, clean_env(), clear=True):
        spec.loader.exec_module(mod)
    return mod


class StyleHookTests(unittest.TestCase):
    def setUp(self):
        self.hook = load_style_hook()

    def test_formal_request_gets_style_and_goes_to_free_chain(self):
        data = {"model": "formal", "messages": [{"role": "user", "content": "q"}]}
        self.assertTrue(self.hook.apply_style(data, "STYLE"))
        self.assertEqual(data["model"], "free")
        self.assertEqual(data["messages"][0], {"role": "system", "content": "STYLE"})
        self.assertEqual(data["messages"][1]["content"], "q")

    def test_existing_system_message_is_kept_after_style(self):
        data = {"model": "formal", "messages": [{"role": "system", "content": "mine"},
                                                {"role": "user", "content": "q"}]}
        self.hook.apply_style(data, "STYLE")
        self.assertEqual(len(data["messages"]), 2)
        self.assertTrue(data["messages"][0]["content"].startswith("STYLE"))
        self.assertTrue(data["messages"][0]["content"].endswith("mine"))

    def test_other_models_are_untouched(self):
        data = {"model": "free", "messages": [{"role": "user", "content": "q"}]}
        self.assertFalse(self.hook.apply_style(data, "STYLE"))
        self.assertEqual(data, {"model": "free", "messages": [{"role": "user", "content": "q"}]})

    def test_frontmatter_is_stripped_from_real_style_file(self):
        style = self.hook.load_style(
            REPO / "plugins/arabic-gov-skills/skills/formal-writing-ar/SKILL.md")
        self.assertFalse(style.startswith("---"))
        self.assertNotIn("description:", style.split("\n")[0])
        self.assertIn("منع الاختلاق", style)


class CloudSetupTests(unittest.TestCase):
    SETUP = REPO / "setup/cloud-setup.sh"

    def test_setup_script_is_valid_bash(self):
        out = subprocess.run(["bash", "-n", str(self.SETUP)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_setup_installs_free_gw_pointing_at_gateway(self):
        text = self.SETUP.read_text(encoding="utf-8")
        self.assertIn('"$BIN/free-gw"', text)
        self.assertIn("plugins/free-llm-gateway/skills/free-llm-gateway/scripts/gateway.py", text)
        self.assertTrue((REPO / "plugins/free-llm-gateway/skills/free-llm-gateway/scripts/gateway.py").exists())

    def test_setup_contains_no_secret(self):
        text = self.SETUP.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"(sk-[A-Za-z0-9-]{16,}|AIza[0-9A-Za-z_-]{20,}|gsk_[A-Za-z0-9]{16,})")


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
