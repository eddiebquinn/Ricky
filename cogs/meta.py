import discord
import utils.utils as utils
import database
from utils.logger import LOGGER
from discord.ext import commands, tasks
from itertools import cycle


class Meta(commands.Cog):

    def __init__(self, client):
        LOGGER.warning(f"initilised {__class__.__cog_name__} cog")
        self.client = client
        self.client.remove_command('help')
        self.status = cycle(["Hi, im ricky!"])
        self.activity_cycle.start()
        self.add_guilds.start()

    @tasks.loop(hours=1)
    async def add_guilds(self):
        """Automatically adds missing guilds to databse every hour"""
        LOGGER.info("Automated guild integrity check starting")
        guilds_member = self.client.guilds
        guilds_databse = [guild_row[0] for guild_row in await database.DATABASE_CONN.select_guild_data()]

        for guild in guilds_member:
            if guild.id in guilds_databse:
                continue
            await database.DATABASE_CONN.insert_guild_data(guild.id)
            LOGGER.warning(
                f"{guild.id} added to databse due to integrity check")

    @tasks.loop(minutes=1)
    async def activity_cycle(self):
        """Cycles through presences every min"""
        await self.client.change_presence(
            status=discord.Status.online, activity=discord.Game(
                next(self.status))
        )

    @commands.command(name="invite")
    @commands.cooldown(1, 10)
    async def invite(self, ctx):
        """Sends bot invite"""
        bot_invite = utils.extract_json(
        )["discord_api_settings"]["invite_link"]
        await ctx.send(bot_invite)

    @commands.command(name="help")
    async def help(self, ctx):
        await ctx.send("https://github.com/eddiebquinn/Ricky/wiki/Bot-commands")


def setup(client):
    client.add_cog(Meta(client))
