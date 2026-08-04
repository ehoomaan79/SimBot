#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${APP_DIR}"

if [[ -x "${APP_DIR}/.venv/bin/python" ]]; then
  # shellcheck disable=SC1091
  source "${APP_DIR}/.venv/bin/activate"
  exec python "${APP_DIR}/bot/bot.py"
fi

exec python3 "${APP_DIR}/bot/bot.py"
