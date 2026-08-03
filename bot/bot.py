import discord
from discord.ext import commands

from reponse_parser import validate_redeem_response
from config import DISCORD_TOKEN
from database import init_db, add_player, player_exists, get_latest_code
from api import redeem
from kingshot_listener import handle_message
from workers import check_codes
import asyncio


intents = discord.Intents.default()

# allows reading messages
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():

    init_db()
    print(
        f"Logged in as {bot.user}"
    )
    asyncio.create_task(
        check_codes()
    )


@bot.event

async def on_message(message):

    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.command()
async def add(
    ctx,
    fid,
    kid
):


    if not fid.isdigit():

        await ctx.send(
            "Invalid player ID"
        )
        return


    if not kid.isdigit():

        await ctx.send(
            "Invalid kingdom ID"
        )
        return

    if player_exists(fid):

        await ctx.send(
            "Player already registered"
        )
        return

    await ctx.send(
        "Checking player..."
    )

    code = get_latest_code()

    if code is None:

        await ctx.send(
            "No active gift codes available"
        )

        return

    response = await redeem(
        fid,
        code,
        kid
    )


    print(response)


    valid = validate_redeem_response(
        response
    )


    if not valid:

        await ctx.send(
            "❌ Invalid player ID or kingdom"
        )

        return



    add_player(
        fid,
        kid,
        str(ctx.author.id)
    )


    await ctx.message.add_reaction(
        "✅"
    )


    await ctx.send(
        f"Player `{fid}` added"
    )

from database import add_code

@bot.command()
@commands.has_permissions(administrator=True)
async def code(ctx, action=None, code=None):

    if action != "add" or code is None:
        await ctx.send(
            "Usage: !code add <giftcode>"
        )
        return


    added = add_code(code)


    if added:
        await ctx.send(
            f"✅ Added gift code `{code}`"
        )

    else:
        await ctx.send(
            f"⚠️ Code `{code}` already exists"
        )

bot.run(DISCORD_TOKEN)