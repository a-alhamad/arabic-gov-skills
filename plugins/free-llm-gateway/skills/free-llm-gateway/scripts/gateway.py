#!/usr/bin/env python3
"""Free LLM gateway: one local OpenAI-compatible endpoint over free-tier providers.

Builds a LiteLLM proxy config from whichever provider keys exist in the
environment, so a provider without a key is simply left out. All requests to
the model name "free" go to the first available provider and fall back to the
next one on rate limits or errors.

Commands:
  providers   list providers and whether their key is set
  config      write the config file and print its path
  start       write the config and start the proxy in the background
  check       call the running proxy with a short request
  stop        stop the proxy
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Order matters: first available provider is the primary for "free".
# Gemini first because it handles Arabic best among the free tiers.
PROVIDERS = [
    ("gemini", "GEMINI_API_KEY", "gemini/gemini-2.5-flash"),
    ("groq", "GROQ_API_KEY", "groq/openai/gpt-oss-120b"),
    ("cerebras", "CEREBRAS_API_KEY", "cerebras/gpt-oss-120b"),
    ("mistral", "MISTRAL_API_KEY", "mistral/mistral-small-latest"),
    ("openrouter", "OPENROUTER_API_KEY", "openrouter/meta-llama/llama-3.3-70b-instruct:free"),
]

HOME = Path(os.environ.get("FREE_GW_HOME", Path.home() / ".free-llm-gateway"))
PORT = int(os.environ.get("FREE_GW_PORT", "4000"))
MASTER_KEY = os.environ.get("FREE_GW_MASTER_KEY", "sk-local-free-gateway")


def model_for(name, default):
    return os.environ.get(f"FREE_GW_{name.upper()}_MODEL", default)


def available():
    return [(n, k, model_for(n, m)) for n, k, m in PROVIDERS if os.environ.get(k)]


def build_config(env_providers):
    if not env_providers:
        raise SystemExit("No provider key found. Set at least one of: "
                         + ", ".join(k for _, k, _ in PROVIDERS))
    model_list = []
    for name, key, model in env_providers:
        model_list.append({"model_name": name,
                           "litellm_params": {"model": model, "api_key": f"os.environ/{key}"}})
    primary_name, primary_key, primary_model = env_providers[0]
    model_list.append({"model_name": "free",
                       "litellm_params": {"model": primary_model,
                                          "api_key": f"os.environ/{primary_key}"}})
    fallbacks = [n for n, _, _ in env_providers[1:]]
    return {
        "model_list": model_list,
        "router_settings": {
            "fallbacks": [{"free": fallbacks}] if fallbacks else [],
            "num_retries": 1,
            "allowed_fails": 1,
            "cooldown_time": 60,
        },
        "litellm_settings": {"drop_params": True, "request_timeout": 120},
        "general_settings": {"master_key": MASTER_KEY},
    }


def write_config():
    HOME.mkdir(parents=True, exist_ok=True)
    path = HOME / "config.yaml"  # JSON is valid YAML
    path.write_text(json.dumps(build_config(available()), indent=2), encoding="utf-8")
    return path


def pid_file():
    return HOME / "proxy.pid"


def running_pid():
    try:
        pid = int(pid_file().read_text())
        os.kill(pid, 0)
        return pid
    except (OSError, ValueError):
        return None


def http(path, body=None, timeout=60):
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {MASTER_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def cmd_providers(_):
    for name, key, model in PROVIDERS:
        state = "set" if os.environ.get(key) else "missing"
        print(f"{name:<11} {key:<20} {state:<8} {model_for(name, model)}")


def cmd_config(_):
    print(write_config())


def cmd_start(_):
    if running_pid():
        print(f"Already running on http://127.0.0.1:{PORT}/v1")
        return
    cfg = write_config()
    log = open(HOME / "proxy.log", "ab")
    proc = subprocess.Popen(["litellm", "--config", str(cfg), "--host", "127.0.0.1",
                             "--port", str(PORT)], stdout=log, stderr=log,
                            start_new_session=True)
    pid_file().write_text(str(proc.pid))
    for _ in range(90):
        if proc.poll() is not None:
            raise SystemExit(f"Proxy exited early. See {HOME / 'proxy.log'}")
        try:
            http("/health/liveliness", timeout=2)
            print(f"Running on http://127.0.0.1:{PORT}/v1  (model: free)")
            return
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(1)
    raise SystemExit(f"Proxy did not answer in time. See {HOME / 'proxy.log'}")


def cmd_check(args):
    try:
        out = http("/v1/chat/completions", {
            "model": args.model,
            "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
            "max_tokens": 10})
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:400]}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Proxy not reachable: {e.reason}. Run: gateway.py start")
    print(f"{out.get('model')}: {out['choices'][0]['message']['content']!r}")


def cmd_stop(_):
    pid = running_pid()
    if not pid:
        print("Not running")
        return
    os.killpg(pid, signal.SIGTERM)
    pid_file().unlink(missing_ok=True)
    print("Stopped")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("providers", "config", "start", "stop"):
        sub.add_parser(name)
    c = sub.add_parser("check")
    c.add_argument("--model", default="free")
    args = p.parse_args(argv)
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
