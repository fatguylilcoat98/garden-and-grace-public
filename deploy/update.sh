#!/usr/bin/env bash
# Pull the latest code, install any new packages, restart.
set -e
cd "$(dirname "$0")/.."
git pull
./.venv/bin/pip install -r backend/requirements.txt
if systemctl list-units --type=service 2>/dev/null | grep -q garden-and-grace; then
  sudo systemctl restart garden-and-grace && echo "✅ Restarted."
else
  echo "✅ Updated. Restart it however you're running it (or set up the service — see deploy/SELF-HOST.md)."
fi
