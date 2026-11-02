#!/usr/bin/env bash
# Setup script for Claude Code cloud environments.
# Paste into: environment settings > Setup script
#   curl -fsSL https://raw.githubusercontent.com/a-alhamad/arabic-gov-skills/main/setup/cloud-setup.sh | bash
# Contains no secrets: provider keys come from the environment's secrets.
set -euo pipefail

# Free LLM gateway runtime (the gateway itself starts on demand via the skill)
if ! command -v litellm >/dev/null 2>&1; then
  pip install --quiet 'litellm[proxy]'
fi

echo "cloud-setup: done"
