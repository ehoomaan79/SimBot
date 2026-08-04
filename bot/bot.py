import asyncio

import discord
from discord.ext import commands

from api import redeem
from config import DISCORD_TOKEN
from database import add_code, add_player, get_active_codes, get_latest_code, init_db, player_exists, remove_code, remove_player
from giftcodes import redeem_all_active_codes_for_player
from logger import get_logger
from reponse_parser import validate_redeem_response
from workers import check_codes


logger = get_logger(__name__)

intents = discord.Intents.default()

# allows reading messages
intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents)


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
    await bot.process_commands(message)


@bot.command(name="add")
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
    if code is not None:
        logger.info("Redeeming code %s for new player %s", code, fid)
        response = await redeem(fid, code, kid)
        logger.debug("Redeem response for %s: %s", fid, response)

        valid = validate_redeem_response(response)
        if not valid:
            logger.warning("Player registration failed for fid=%s kid=%s. Response: %s", fid, kid, response)
            await ctx.send("❌ Invalid player ID or kingdom. Please double-check the values.")
            return

    added = add_player(fid, kid, str(ctx.author.id))
    if not added:
        await ctx.send(f"⚠️ Player `{fid}` was not added due to a database conflict.")
        return

    await ctx.message.add_reaction("✅")
    await ctx.send(f"✅ Player `{fid}` added successfully.")

    active_codes = get_active_codes()
    if active_codes:
        await redeem_all_active_codes_for_player(fid, kid)
        await ctx.send(f"🔄 I also started redeeming {len(active_codes)} active gift code(s) for this player.")
    else:
        await ctx.send("ℹ️ No active gift codes are currently available for redemption.")


@bot.command(name="remove")
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


@bot.command(name="code")
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


@bot.command(name="status")
async def status_command(ctx):
    logger.info("Status command invoked by %s", ctx.author)
    active_codes = get_active_codes()
    await ctx.send(f"📊 Active gift codes: {len(active_codes)}")


bot.run(DISCORD_TOKEN)