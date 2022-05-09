from discord.ext import commands
import traceback
import sys

class ErrorHandler(commands.Cog):

    def __init__(self, client):
        print(f"initilised {__class__.__cog_name__} cog")
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)
        if isinstance(error, commands.CommandOnCooldown):
            time =  int(error.retry_after) // 60
            await ctx.send(content=f'This command is on cooldown. Please wait {time}m', delete_after=5)

        else:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(client):
    client.add_cog(ErrorHandler(client))
