#!/usr/bin/env bash
# One-time setup: make a Python environment and install everything.
set -e
cd "$(dirname "$0")/.."
echo "→ Creating Python environment..."
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip >/dev/null
echo "→ Installing packages (this takes a minute)..."
./.venv/bin/pip install -r backend/requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "→ Made a .env file for you."
fi
echo ""
echo "✅ Setup done."
echo "   Next: open .env, paste your ANTHROPIC_API_KEY, save — then run deploy/run.sh"
