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
  read -t 1 -n 10000 purge_buffer
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

if [[ -f "${INSTALL_DIR}/requirements.txt" ]]; then
  python3 -m venv "${INSTALL_DIR}/.venv"
  "${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip || true
  "${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" || true
else
  echo "requirements.txt not found; skipping dependency installation."
fi

touch "${INSTALL_DIR}/.env"

if [[ "${SYSTEMD_MODE}" == "system" ]]; then
  mkdir -p /etc/systemd/system
  cp "${INSTALL_DIR}/scripts/discord-bot.service" "${SERVICE_FILE}"
  sed -i "s|__INSTALL_DIR__|${INSTALL_DIR}|g" "${SERVICE_FILE}"
  sed -i "s|__PYTHON_EXEC__|${INSTALL_DIR}/.venv/bin/python|g" "${SERVICE_FILE}"
  sed -i "s|__BOT_PATH__|${INSTALL_DIR}/bot/bot.py|g" "${SERVICE_FILE}"

  echo "Installation completed."
  echo ""
  echo "First run the bot once to enter the required values:"
  echo "  bash: sudo BOT_SETUP_MODE=1 ${INSTALL_DIR}/.venv/bin/python ${INSTALL_DIR}/bot/bot.py"
  echo "  fish: sudo env BOT_SETUP_MODE=1 ${INSTALL_DIR}/.venv/bin/python ${INSTALL_DIR}/bot/bot.py"
  echo "  zsh: sudo BOT_SETUP_MODE=1 ${INSTALL_DIR}/.venv/bin/python ${INSTALL_DIR}/bot/bot.py"
  echo ""
  echo "Then enable and start the service with:"
  echo "  sudo systemctl daemon-reload"
  echo "  sudo systemctl enable ${SERVICE_NAME}.service"
  echo "  sudo systemctl start ${SERVICE_NAME}.service"
  echo "  sudo systemctl status ${SERVICE_NAME}.service --no-pager"
elif [[ "${SYSTEMD_MODE}" == "user" ]]; then
  mkdir -p "$HOME/.config/systemd/user"
  cp "${INSTALL_DIR}/scripts/discord-bot.service" "${SERVICE_FILE}"
  sed -i "s|__INSTALL_DIR__|${INSTALL_DIR}|g" "${SERVICE_FILE}"
  sed -i "s|__PYTHON_EXEC__|${INSTALL_DIR}/.venv/bin/python|g" "${SERVICE_FILE}"
  sed -i "s|__BOT_PATH__|${INSTALL_DIR}/bot/bot.py|g" "${SERVICE_FILE}"

  echo "Installation completed."
  echo ""
  echo "First run the bot once to enter the required values:"
  echo "  bash: sudo BOT_SETUP_MODE=1 ${INSTALL_DIR}/.venv/bin/python ${INSTALL_DIR}/bot/bot.py"
  echo "  fish: sudo env BOT_SETUP_MODE=1 ${INSTALL_DIR}/.venv/bin/python ${INSTALL_DIR}/bot/bot.py"
  echo "  zsh: sudo BOT_SETUP_MODE=1 ${INSTALL_DIR}/.venv/bin/python ${INSTALL_DIR}/bot/bot.py"
  echo ""
  echo "Then enable and start the service with:"
  echo "  systemctl --user daemon-reload"
  echo "  systemctl --user enable ${SERVICE_NAME}.service"
  echo "  systemctl --user start ${SERVICE_NAME}.service"
  echo "  systemctl --user status ${SERVICE_NAME}.service --no-pager"
else
  echo "Installation completed."
  echo ""
  echo "Start the bot manually with:"
  echo "  ${INSTALL_DIR}/.venv/bin/python ${INSTALL_DIR}/bot/bot.py"
fi
