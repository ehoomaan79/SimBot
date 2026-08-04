#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

read_env_value() {
  local key="$1"
  if [[ -f "${APP_DIR}/.env" ]]; then
    python3 - "${APP_DIR}/.env" "$key" <<'PY'
import sys
from pathlib import Path

env_path = Path(sys.argv[1])
key = sys.argv[2]

if env_path.exists():
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(f"{key}="):
            print(stripped.split("=", 1)[1].strip())
            break
PY
  fi
}

write_env_value() {
  local key="$1"
  local value="$2"
  python3 - "${APP_DIR}/.env" "$key" "$value" <<'PY'
import sys
from pathlib import Path

env_path = Path(sys.argv[1])
key = sys.argv[2]
value = sys.argv[3]

lines = []
if env_path.exists():
    lines = env_path.read_text().splitlines()

new_line = f"{key}={value}"
found = False
for index, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith(f"{key}="):
        lines[index] = new_line
        found = True
        break

if not found:
    lines.append(new_line)

env_path.write_text("\n".join(lines) + "\n")
PY
}

prompt_for_env_value() {
  local key="$1"
  local prompt_text="$2"
  local default_value="$3"
  local existing_value

  existing_value="$(read_env_value "$key" || true)"
  if [[ -n "$existing_value" ]]; then
    return 0
  fi

  echo "$prompt_text"
  if [[ -n "$default_value" ]]; then
    echo "Using default: $default_value"
  fi

  local value=""
  if [[ -r /dev/tty ]]; then
    read -r value </dev/tty
  elif [[ -t 0 ]]; then
    read -r value
  fi

  if [[ -z "$value" ]]; then
    value="$default_value"
  fi

  if [[ -n "$value" ]]; then
    write_env_value "$key" "$value"
  fi
}

ensure_env_values() {
  touch "${APP_DIR}/.env"

  prompt_for_env_value "DISCORD_TOKEN" "Enter the Discord bot token: " ""
  if [[ -z "$(read_env_value DISCORD_TOKEN || true)" ]]; then
    echo "Bot token cannot be empty." >&2
    exit 1
  fi

  prompt_for_env_value "SIGN_SECRET" "Enter the Kingshot signing secret [default: mN4!pQs6JrYwV9]: " "mN4!pQs6JrYwV9"
  prompt_for_env_value "API_URL" "Enter the Kingshot API URL [default: https://kingshot-giftcode.centurygame.com/api/gift_code]: " "https://kingshot-giftcode.centurygame.com/api/gift_code"
}

cd "${APP_DIR}"
ensure_env_values

if [[ -x "${APP_DIR}/.venv/bin/python" ]]; then
  # shellcheck disable=SC1091
  source "${APP_DIR}/.venv/bin/activate"
  exec python "${APP_DIR}/bot/bot.py"
fi

exec python3 "${APP_DIR}/bot/bot.py"
