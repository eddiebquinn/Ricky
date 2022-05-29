import discord
import utils.utils as utils
from utils.logger import LOGGER
from discord.ext import commands, tasks
from itertools import cycle


class Meta(commands.Cog):

    def __init__(self, client):
        LOGGER.warning(f"initilised {__class__.__cog_name__} cog")
        self.client = client
        self.status = cycle(["Hi, im ricky!"])
        self.activity_cycle.start()

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


def setup(client):
    client.add_cog(Meta(client))
