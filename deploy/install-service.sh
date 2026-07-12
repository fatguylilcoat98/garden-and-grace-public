#!/usr/bin/env bash
# One-command installer: makes Garden & Grace an always-on service.
# Starts on boot, restarts if it crashes, reads keys from .env — like Render,
# but on your own box. Run it once with sudo:
#
#     sudo bash deploy/install-service.sh
#
set -e

# --- figure out who and where automatically (no hand-editing) -------------
RUN_USER="${SUDO_USER:-$(whoami)}"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_UVICORN="$APP_DIR/.venv/bin/uvicorn"
ENV_FILE="$APP_DIR/.env"
UNIT=/etc/systemd/system/garden-and-grace.service

echo "User:      $RUN_USER"
echo "App folder: $APP_DIR"

# --- sanity checks --------------------------------------------------------
if [ ! -x "$VENV_UVICORN" ]; then
  echo "!! Can't find $VENV_UVICORN"
  echo "   Run  bash deploy/setup.sh  first, then re-run this."
  exit 1
fi
if [ ! -f "$ENV_FILE" ]; then
  echo "!! No .env file yet. Run  bash deploy/setup.sh  first."
  exit 1
fi

# --- make sure a PORT is set (default 8001, clear of Claspion on 8000) ----
if ! grep -q '^PORT=' "$ENV_FILE"; then
  printf '\nPORT=8001\n' >> "$ENV_FILE"
  echo "Added PORT=8001 to .env"
fi
PORT_VAL="$(grep '^PORT=' "$ENV_FILE" | tail -1 | cut -d= -f2)"

# --- write the systemd unit with the real paths filled in -----------------
cat > "$UNIT" <<EOF
[Unit]
Description=Garden & Grace (Public)
After=network.target

[Service]
WorkingDirectory=$APP_DIR
User=$RUN_USER
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_UVICORN backend.main:app --host 0.0.0.0 --port \${PORT}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "Wrote $UNIT"

# --- turn it on -----------------------------------------------------------
systemctl daemon-reload
systemctl enable --now garden-and-grace

echo
echo "Done. Garden & Grace is now a background service on port ${PORT_VAL:-8001}."
echo "It will start automatically on boot and restart itself if it crashes."
echo
systemctl status garden-and-grace --no-pager || true
echo
echo "Open:  http://100.90.72.114:${PORT_VAL:-8001}"
echo "Logs:  sudo journalctl -u garden-and-grace -f"
echo "Stop:  sudo systemctl stop garden-and-grace"
