#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/ehoomaan79/SimBot.git}"
INSTALL_DIR="${INSTALL_DIR:-/opt/discord-bot}"
CLONE_DIR="${CLONE_DIR:-/tmp/discord-bot-src}"
SERVICE_NAME="discord-bot"
SERVICE_FILE=""
SYSTEMD_MODE="none"

install_pkg() {
  local pkg="$1"
  echo "Installing package: $pkg"
  if command -v apt-get >/dev/null 2>&1; then
    echo "Using apt-get"
    apt-get update
    apt-get install -y "$pkg"
  elif command -v yum >/dev/null 2>&1; then
    echo "Using yum"
    yum install -y "$pkg"
  elif command -v dnf >/dev/null 2>&1; then
    echo "Using dnf"
    dnf install -y "$pkg"
  elif command -v apk >/dev/null 2>&1; then
    echo "Using apk"
    apk add --no-cache "$pkg"
  else
    echo "No supported package manager found."
  fi
}

ensure_command() {
  local cmd="$1"
  local pkg="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing $cmd. Attempting to install $pkg..."
    install_pkg "$pkg"
  fi

  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Could not install $cmd automatically. Please install $pkg manually." >&2
    exit 1
  fi
}

ensure_command git git
ensure_command python3 python3
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "python3 venv support is missing. Attempting to install a venv package..."
  install_pkg "python3-venv"
  if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "python3 venv support is still unavailable. Please install the venv package for your distro manually." >&2
    exit 1
  fi
fi
ensure_command curl curl || true

if command -v systemctl >/dev/null 2>&1; then
  if [[ $EUID -eq 0 ]]; then
    SYSTEMD_MODE="system"
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
  elif systemctl --user list-units >/dev/null 2>&1; then
    SYSTEMD_MODE="user"
    INSTALL_DIR="${INSTALL_DIR:-$HOME/discord-bot}"
    SERVICE_FILE="$HOME/.config/systemd/user/${SERVICE_NAME}.service"
  fi
fi

if [[ "${SYSTEMD_MODE}" == "none" ]]; then
  echo "systemd was not detected; the bot will be installed to ${INSTALL_DIR}, but no service will be enabled."
fi

read -r -p "Enter the Discord bot token: " DISCORD_TOKEN
if [[ -z "${DISCORD_TOKEN}" ]]; then
  echo "Bot token cannot be empty." >&2
  exit 1
fi

read -r -p "Enter the Kingshot signing secret [default: mN4!pQs6JrYwV9]: " SIGN_SECRET
SIGN_SECRET="${SIGN_SECRET:-mN4!pQs6JrYwV9}"

read -r -p "Enter the Kingshot API URL [default: https://kingshot-giftcode.centurygame.com/api/gift_code]: " API_URL
API_URL="${API_URL:-https://kingshot-giftcode.centurygame.com/api/gift_code}"

rm -rf "${INSTALL_DIR}" "${CLONE_DIR}"
mkdir -p "${INSTALL_DIR}" "${CLONE_DIR}" "${INSTALL_DIR}/logs"

if git clone "${REPO_URL}" "${CLONE_DIR}"; then
  echo "Repository cloned to ${CLONE_DIR}"
else
  echo "Failed to clone repository from ${REPO_URL}; continuing with local files if present." >&2
fi

if [[ -d "${CLONE_DIR}" ]]; then
  cp -a "${CLONE_DIR}/." "${INSTALL_DIR}/"
else
  echo "Clone directory not available; copying from current working directory instead." >&2
  cp -a . "${INSTALL_DIR}/"
fi

chmod +x "${INSTALL_DIR}/scripts/start_discord_bot.sh"

if [[ -f "${INSTALL_DIR}/requirements.txt" ]]; then
  python3 -m venv "${INSTALL_DIR}/.venv"
  "${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip || true
  "${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" || true
else
  echo "requirements.txt not found; skipping dependency installation."
fi

cat > "${INSTALL_DIR}/.env" <<EOF
DISCORD_TOKEN=${DISCORD_TOKEN}
SIGN_SECRET=${SIGN_SECRET}
API_URL=${API_URL}
EOF

if [[ "${SYSTEMD_MODE}" == "system" ]]; then
  mkdir -p /etc/systemd/system
  cat > "${SERVICE_FILE}" <<EOF2
[Unit]
Description=Discord Kingshot gift code bot
After=network.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=${INSTALL_DIR}/.env
ExecStart=${INSTALL_DIR}/scripts/start_discord_bot.sh
Restart=always
RestartSec=5
StandardOutput=append:${INSTALL_DIR}/logs/discord-bot.log
StandardError=append:${INSTALL_DIR}/logs/discord-bot.error.log

[Install]
WantedBy=multi-user.target
EOF2

  systemctl daemon-reload || true
  systemctl enable --now "${SERVICE_NAME}.service" || true
  systemctl status "${SERVICE_NAME}.service" --no-pager || true
elif [[ "${SYSTEMD_MODE}" == "user" ]]; then
  mkdir -p "$HOME/.config/systemd/user"
  cat > "${SERVICE_FILE}" <<EOF2
[Unit]
Description=Discord Kingshot gift code bot
After=network.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=${INSTALL_DIR}/.env
ExecStart=${INSTALL_DIR}/scripts/start_discord_bot.sh
Restart=always
RestartSec=5
StandardOutput=append:${INSTALL_DIR}/logs/discord-bot.log
StandardError=append:${INSTALL_DIR}/logs/discord-bot.error.log

[Install]
WantedBy=default.target
EOF2

  systemctl --user daemon-reload || true
  systemctl --user enable --now "${SERVICE_NAME}.service" || true
  systemctl --user status "${SERVICE_NAME}.service" --no-pager || true
else
  echo "Installation completed. Start the bot manually with:"
  echo "  ${INSTALL_DIR}/scripts/start_discord_bot.sh"
fi
