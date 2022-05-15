import discord
from discord.ext import commands
import utils.utils as utils
import utils.logger as logger
import os

intents = discord.Intents.all()
intents.members = True
intents.presences = True

client = commands.Bot(command_prefix="!", intents=intents,
                      case_insensitive=True)


@client.event
async def on_ready():
    """Waits until the client’s internal cache is all ready, and then loads cogs"""
    await client.wait_until_ready()
    await cogs_load()
    logger.LOGGER.warning("Bot is active")


async def cogs_load():
    """Loops through files in cogs file, and loads them"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")


def launch_discord_bot():
    """Initalises the discord bot"""
    token = utils.extract_json()["discord_api_settings"]["api_token"]
    client.run(token)
