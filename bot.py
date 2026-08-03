import discord
from discord.ext import commands

from dotenv import load_dotenv
import os

from api import redeem


load_dotenv()


TOKEN=os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content=True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )



@bot.command()
async def redeemcode(ctx, fid, code, kid):

    await ctx.send(
        "Redeeming..."
    )

    result = await redeem(
        fid,
        code,
        kid
    )

    await ctx.send(
        f"```{result[:1900]}```"
    )


bot.run(TOKEN)