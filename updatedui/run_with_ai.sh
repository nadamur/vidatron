#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$ROOT/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

if [[ -f "$REPO/vidatron_ai/venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$REPO/vidatron_ai/venv/bin/activate"
elif [[ -f "$ROOT/venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/venv/bin/activate"
else
  echo "No venv found. Run:"
  echo "  cd $REPO/vidatron_ai && python3 -m venv venv && source venv/bin/activate"
  echo "  pip install -r requirements.txt && pip install -r $ROOT/requirements.txt"
  exit 1
fi

cd "$ROOT"
exec python main.py
