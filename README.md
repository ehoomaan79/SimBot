# Discord Kingshot Gift Code Bot

A Discord bot that monitors a shared Kingshot gift-code channel, stores newly discovered codes, and redeems them for registered players. It is designed for a small community or personal bot setup where gift codes are shared in Discord and should be redeemed automatically.

## What this bot does

- Watches a configured Kingshot Discord channel for gift-code announcements
- Extracts gift codes and expiry information from posted messages
- Stores gift codes in a local SQLite database
- Redeems codes for registered players when new codes are detected
- Supports adding new players from Discord commands
- Logs important activity to the terminal and to a daily rotating log file
- Can run as a Linux service so it starts automatically after boot

## Features

- Automatic gift-code detection from Discord messages
- Expiry awareness for stored gift codes
- Database-backed player registration
- Async redeem attempts for many players
- Structured logging for debugging and monitoring
- Linux service integration with systemd

## Installation

Use the one-line installation command below on a Linux host with `sudo` access:

```bash
curl -fsSL https://raw.githubusercontent.com/ehoomaan79/SimBot/main/install.sh | sudo bash
```

This installer will:

- clone the repository into a system path under `/opt/discord-bot-src`
- copy the project into `/opt/discord-bot`
- create the required runtime folders such as `/opt/discord-bot/logs`
- create or update `/opt/discord-bot/.env` with your Discord token and the Kingshot API values
- install and enable the systemd service
- start the bot automatically

## Project structure

- bot/ - main bot logic, Discord commands, API integration, and database helpers
- docs/ - public-facing documentation and terms page
- scripts/ - service startup script and systemd unit file
- install.sh - installer for deploying the bot on a Linux host

## Requirements

- Linux host (Ubuntu/Debian-style system recommended)
- Python 3.10+
- A Discord bot token
- Access to the Kingshot gift-code API endpoint
- A working network connection to Discord and the Kingshot API

## Environment variables

Create a .env file in the project root with the following values:

```env
DISCORD_TOKEN=your_discord_bot_token
SIGN_SECRET=your_kingshot_signature_secret
API_URL=https://kingshot-giftcode.centurygame.com/api/gift_code
```

### Required environment values

The installer prompts for the Discord bot token and writes these values into `/opt/discord-bot/.env`:

```env
DISCORD_TOKEN=your_discord_bot_token
SIGN_SECRET=your_kingshot_signature_secret
API_URL=https://kingshot-giftcode.centurygame.com/api/gift_code
```

### Service management

After installation, you can manage the bot with:

```bash
systemctl --user status discord-bot
systemctl --user restart discord-bot
systemctl --user stop discord-bot
```

## Uninstallation

To remove the installed service and files:

```bash
sudo rm -f /etc/systemd/system/discord-bot.service
sudo rm -rf /opt/discord-bot /opt/discord-bot-src
sudo systemctl daemon-reload
```

If you installed the service as a user service instead of a system service, use the user variant:

```bash
systemctl --user disable --now discord-bot
rm -f ~/.config/systemd/user/discord-bot.service
systemctl --user daemon-reload
```

## Discord commands

The bot currently supports these basic commands:

- !add <fid> <kid> - register a player and attempt a redemption with the latest active gift code
- !code add <giftcode> - manually add a gift code to the database

## Logging

The bot writes logs to both:

- the terminal console
- a log file in the project root named bot.log

The service also writes its own runtime logs under the logs directory.

## Privacy and data handling

The bot stores the following information locally in SQLite:

- Discord user IDs
- Kingshot player IDs
- Kingdom IDs
- Gift codes and expiry timestamps

This data is used only to support redeeming gift codes for registered players. If you deploy the bot publicly, make sure you are comfortable with the data you are storing and the terms you provide to users.

## Disclaimer

This project is not officially affiliated with Discord, Century Games, Kingshot, or the Kingshot gift-code service. It is a community-driven automation helper meant for personal or community use.

## Support

If you need help with setup, deployment, or troubleshooting, open an issue in the repository or contact the maintainer listed in the terms page.