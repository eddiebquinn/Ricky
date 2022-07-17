import discord
from discord.ext import commands
from utils.logger import LOGGER
import traceback
import sys


class ErrorHandler(commands.Cog):

    def __init__(self, client):
        LOGGER.warning(f"initialised {__class__.__cog_name__} cog")
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Captures errors as they happen and deals with them"""
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.errors.CheckFailure):
            return
        if isinstance(error, discord.errors.Forbidden):
            return
        if isinstance(error, commands.CommandOnCooldown):
            time = int(error.retry_after) // 60
            await ctx.send(content=f'This command is on cooldown. Please wait {time}m', delete_after=5)

        else:
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
            LOGGER.error(
                f'Command: {ctx.command}, {type(error)}, {error}, {error.__traceback__}', exc_info=True)


def setup(client):
    client.add_cog(ErrorHandler(client))
