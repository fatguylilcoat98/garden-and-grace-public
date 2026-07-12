#!/usr/bin/env bash
# Run the app. Reads settings from .env. Ctrl+C to stop.
set -e
cd "$(dirname "$0")/.."
set -a; [ -f .env ] && . ./.env; set +a
echo "🌿 Garden & Grace starting on port ${PORT:-8001} ..."
exec ./.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8001}"
