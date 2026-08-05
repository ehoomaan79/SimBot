import asyncio
import os
import sys
from pathlib import Path

# Import config which will prompt for missing values and set them in os.environ
from config import DISCORD_TOKEN

# Load .env and initialize config FIRST before importing other modules
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)

import discord
from discord.ext import commands

# Now import other modules that depend on env vars being set
from api import redeem
from database import add_code, add_player, get_active_codes, get_gift_channel_id, get_latest_code, init_db, player_exists, remove_code, remove_player, set_gift_channel_id
from giftcodes import redeem_all_active_codes_for_player
from logger import get_logger
from reponse_parser import classify_redeem_response
from workers import check_codes
from kingshot_listener import handle_message

logger = get_logger(__name__)

intents = discord.Intents.default()

# allows reading messages
intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.command(name="help")
async def help_command(ctx):
    help_text = """```md
Commands:
- !add <fid> <kid>      Register a new player and attempt a redeem with the latest active code.
- !remove <fid>        Remove a registered player.
- !code add <giftcode> Add a gift code to the database. (Admin only)
- !code remove <giftcode> Remove a gift code from the database. (Admin only)
- !setchannel <#channel> or <channel_id> Link the gift-code source channel.
- !status              Show active gift codes and the monitored channel.

Examples:
- !add 123456 123
- !code add SimBot
- !setchannel #gift-codes
```"""
    await ctx.send(help_text)


@bot.event
async def on_ready():
    init_db()
    logger.info("Bot is ready. Logged in as %s", bot.user)
    asyncio.create_task(check_codes())


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    logger.debug(
        "Received message from %s in #%s: %s",
        message.author,
        getattr(message.channel, "name", message.channel.id),
        message.content,
    )

    await handle_message(message)
    await bot.process_commands(message)


@bot.command(name="add", help="Register a new player and attempt a redeem with the latest active gift code.")
async def add_player_command(ctx, fid, kid):
    logger.info("Add-player command invoked by %s for fid=%s kid=%s", ctx.author, fid, kid)

    if not fid.isdigit():
        logger.warning("Invalid player ID '%s' from %s", fid, ctx.author)
        await ctx.send("❌ Invalid player ID. Please provide a numeric fid.")
        return

    if not kid.isdigit():
        logger.warning("Invalid kingdom ID '%s' from %s", kid, ctx.author)
        await ctx.send("❌ Invalid kingdom ID. Please provide a numeric kid.")
        return

    if player_exists(fid):
        logger.warning("Player %s already registered", fid)
        await ctx.send(f"⚠️ Player `{fid}` is already registered.")
        return

    await ctx.send(f"⏳ Checking player `{fid}` and redeeming available gift codes...")

    code = get_latest_code()
    player_added = False
    
    if code is not None:
        logger.info("Redeeming code %s for new player %s", code, fid)
        response = await redeem(fid, code, kid)
        logger.debug("Redeem response for %s: %s", fid, response)

        result = classify_redeem_response(response)
        if not result["valid"]:
            logger.warning(
                "Player registration failed for fid=%s kid=%s. Reason=%s message=%s",
                fid,
                kid,
                result["reason"],
                result["message"],
            )

            if result["reason"] == "code_expired":
                await ctx.send("❌ The current gift code has expired. Please try again later.")
            elif result["reason"] == "code_invalid":
                await ctx.send("❌ The gift code is invalid or could not be found.")
            elif result["reason"] == "player_invalid":
                await ctx.send("❌ Invalid player ID or kingdom. Please double-check the values.")
            else:
                await ctx.send("❌ The redeem request failed. Please try again later.")
        
        if result["reason"] != "player_invalid":
            added = add_player(fid, kid, str(ctx.author.id))
            if not added:
                await ctx.send(f"⚠️ Player `{fid}` was not added due to a database conflict.")
                return

            await ctx.message.add_reaction("✅")
            await ctx.send(f"✅ Player `{fid}` added successfully.")
            player_added = True
    else:
        # No active code available, just register the player
        logger.info("No active gift code available, registering player %s without redemption", fid)
        added = add_player(fid, kid, str(ctx.author.id))
        if not added:
            await ctx.send(f"⚠️ Player `{fid}` was not added due to a database conflict.")
            return

        await ctx.message.add_reaction("✅")
        await ctx.send(f"✅ Player `{fid}` added successfully.")
        player_added = True

    if player_added:
        active_codes = get_active_codes()
        if active_codes:
            await redeem_all_active_codes_for_player(fid, kid)
            await ctx.send(f"🔄 I also started redeeming {len(active_codes)} active gift code(s) for this player.")
        else:
            await ctx.send("ℹ️ No active gift codes are currently available for redemption.")


@bot.command(name="remove", help="Remove a registered player from the database.")
async def remove_player_command(ctx, fid):
    logger.info("Remove-player command invoked by %s for fid=%s", ctx.author, fid)

    if not fid.isdigit():
        await ctx.send("❌ Invalid player ID. Please provide a numeric fid.")
        return

    removed = remove_player(fid)
    if removed:
        await ctx.send(f"✅ Player `{fid}` removed from the database.")
    else:
        await ctx.send(f"⚠️ Player `{fid}` was not found.")


@bot.command(name="code", help="Add or remove a gift code from the database. Admin only.")
@commands.has_permissions(administrator=True)
async def code_command(ctx, action=None, code=None):
    logger.info("Code command invoked by %s with action=%s", ctx.author, action)

    if action == "add" and code:
        added = add_code(code)
        if added:
            logger.info("Admin %s added gift code %s", ctx.author, code)
            await ctx.send(f"✅ Added gift code `{code}` to the database.")
        else:
            logger.warning("Gift code %s already exists", code)
            await ctx.send(f"⚠️ Code `{code}` already exists.")
        return

    if action == "remove" and code:
        removed = remove_code(code)
        if removed:
            await ctx.send(f"✅ Gift code `{code}` removed from the database.")
        else:
            await ctx.send(f"⚠️ Gift code `{code}` was not found.")
        return

    await ctx.send("Usage: `!code add <giftcode>` or `!code remove <giftcode>`")


@bot.command(name="setchannel", help="Link the Discord channel that should be watched for new gift-code messages.")
async def set_channel_command(ctx, channel=None):
    logger.info("Set-channel command invoked by %s", ctx.author)

    if channel is None:
        channel_id = str(ctx.channel.id)
        target_name = ctx.channel.name
    else:
        if channel.startswith("<#") and channel.endswith(">"):
            channel_id = channel[2:-1]
        elif channel.isdigit():
            channel_id = channel
        else:
            if ctx.guild:
                matches = [ch for ch in ctx.guild.channels if ch.name.lower() == channel.lower()]
                if matches:
                    channel_id = str(matches[0].id)
                    target_name = matches[0].name
                else:
                    await ctx.send("❌ I could not find that channel. Please use a channel mention or ID.")
                    return
            else:
                await ctx.send("❌ Please provide a channel mention or ID.")
                return

        target_name = channel

    set_gift_channel_id(channel_id)
    await ctx.send(f"✅ Gift-code channel linked to {target_name} ({channel_id})")


@bot.command(name="status", help="Show the number of active gift codes and the currently monitored channel.")
async def status_command(ctx):
    logger.info("Status command invoked by %s", ctx.author)
    active_codes = get_active_codes()
    configured_channel = get_gift_channel_id() or "not set"
    await ctx.send(f"📊 Active gift codes: {len(active_codes)}\n📍 Monitored channel: {configured_channel}")


try:
    bot.run(DISCORD_TOKEN)
except Exception as exc:
    logger.exception("Discord login failed: %s", exc)
    raise