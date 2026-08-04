#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/ehoomaan79/SimBot.git}"
INSTALL_DIR="/opt/discord-bot"
CLONE_DIR="/tmp/discord-bot-src"
SERVICE_NAME="discord-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ $EUID -ne 0 ]]; then
  echo "This installer must be run as root." >&2
  exit 1
fi

read -r -p "Enter the Discord bot token: " DISCORD_TOKEN
if [[ -z "${DISCORD_TOKEN}" ]]; then
  echo "Bot token cannot be empty." >&2
  exit 1
fi

rm -rf "${INSTALL_DIR}" "${CLONE_DIR}"
mkdir -p "${INSTALL_DIR}" "${CLONE_DIR}" /var/log/discord-bot

if git clone "${REPO_URL}" "${CLONE_DIR}"; then
  echo "Repository cloned to ${CLONE_DIR}"
else
  echo "Failed to clone repository from ${REPO_URL}" >&2
  exit 1
fi

cp -a "${CLONE_DIR}/." "${INSTALL_DIR}/"
cp "${INSTALL_DIR}/scripts/discord-bot.service" "${SERVICE_FILE}"

cat > "${INSTALL_DIR}/.env" <<EOF
DISCORD_TOKEN=${DISCORD_TOKEN}
SIGN_SECRET=mN4!pQs6JrYwV9
API_URL=https://kingshot-giftcode.centurygame.com/api/gift_code
EOF

chmod +x "${INSTALL_DIR}/scripts/start_discord_bot.sh"
mkdir -p "${INSTALL_DIR}/logs"

systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"

systemctl status "${SERVICE_NAME}.service" --no-pager
