#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="/Users/deb/Development/GenAI/ImmigrationChatbot"
cd "$ROOT_DIR"

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

exec "$PYTHON_BIN" -m uvicorn immigration_chatbot.api:app --host 0.0.0.0 --port 8000
