#!/usr/bin/env bash
# Setup script for Claude Code cloud environments.
# Paste into: environment settings > Setup script
#   curl -fsSL https://raw.githubusercontent.com/a-alhamad/arabic-gov-skills/main/setup/cloud-setup.sh | bash
# Contains no secrets: provider keys come from the environment's secrets.
#
# Result in every new session: the command `free-gw` (start | check | stop | providers),
# with the formal-writing-ar style available as model "formal".
set -euo pipefail

REPO_URL="https://github.com/a-alhamad/arabic-gov-skills"
DIR="${FREE_GW_TOOLKIT_DIR:-$HOME/.a-alhamad-toolkit}"
BIN="${FREE_GW_BIN_DIR:-/usr/local/bin}"

# 1. Toolkit checkout (gateway script + style skill), refreshed on every setup
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" pull --quiet --ff-only
else
  git clone --quiet --depth 1 "$REPO_URL" "$DIR"
fi

# 2. Gateway runtime
if ! command -v litellm >/dev/null 2>&1; then
  pip install --quiet 'litellm[proxy]'
fi

# 3. `free-gw` command on PATH
mkdir -p "$BIN" 2>/dev/null || true
if [ ! -w "$BIN" ]; then
  BIN="$HOME/.local/bin"
  mkdir -p "$BIN"
fi
cat > "$BIN/free-gw" <<WRAP
#!/usr/bin/env bash
exec python3 "$DIR/plugins/free-llm-gateway/skills/free-llm-gateway/scripts/gateway.py" "\$@"
WRAP
chmod +x "$BIN/free-gw"

echo "cloud-setup: done. Run: free-gw start && free-gw check --model formal"
