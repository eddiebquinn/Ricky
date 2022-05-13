import discord
from discord.ext import commands
import utils
import os

intents = discord.Intents.all()
intents.members = True
intents.presences = True

client = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

@client.event
async def on_ready():
    await client.wait_until_ready()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Complaints in DMs."))
    await cogs_load()
    print("Bot is active")

async def cogs_load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

def launch_discord_bot():
    token = utils.extract_json()["discord_api_settings"]["api_token"]
    client.run(token)
