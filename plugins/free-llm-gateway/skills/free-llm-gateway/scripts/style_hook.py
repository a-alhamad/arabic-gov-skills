"""LiteLLM proxy hook: requests to model "formal" get the formal-writing-ar
style as a system message, then go through the "free" fallback chain.

Loaded by the proxy from the gateway home directory; the style text is read
once from the file named in FREE_GW_STYLE_FILE (set by gateway.py).
"""
import os

try:
    from litellm.integrations.custom_logger import CustomLogger
except ImportError:  # lets the pure helpers be tested without LiteLLM
    CustomLogger = object

STYLE_MODEL = "formal"
TARGET_MODEL = "free"


def strip_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:].lstrip()
    return text


def load_style(path):
    with open(path, encoding="utf-8") as f:
        return strip_frontmatter(f.read())


def apply_style(data, style):
    """Mutate a chat request in place. Returns True if the style was applied."""
    if data.get("model") != STYLE_MODEL:
        return False
    messages = list(data.get("messages") or [])
    if messages and messages[0].get("role") == "system":
        messages[0] = {**messages[0],
                       "content": style + "\n\n---\n\n" + str(messages[0].get("content", ""))}
    else:
        messages.insert(0, {"role": "system", "content": style})
    data["messages"] = messages
    data["model"] = TARGET_MODEL
    return True


class StyleHook(CustomLogger):
    def __init__(self):
        super().__init__()
        path = os.environ.get("FREE_GW_STYLE_FILE")
        self.style = load_style(path) if path else None

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        if self.style and call_type in ("completion", "acompletion"):
            apply_style(data, self.style)
        return data


proxy_handler_instance = StyleHook()
