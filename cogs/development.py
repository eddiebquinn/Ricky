from discord.ext import commands
import utils


class Development(commands.Cog):
    def __init__(self, client):
        print(f"initilised {__class__.__cog_name__} cog")
        self.client = client

    @commands.command(name="cog", aliases=["cogs"])
    @commands.check(utils.is_developer)
    async def cog(self, ctx, action: str, *args):
        """Command to manually toggle cogs.

        Args:
            action (str): Valid actions are load, unload, reload
            args (str): The cogs you want to perform and action on
        """
        for arg in args:
            if action == "load":
                self.client.load_extension(f"cogs.{arg}")
            elif action == "unload":
                self.client.unload_extension(f"cogs.{arg}")
            elif action == "reload":
                self.client.reload_extension(f"cogs.{arg}")
            else:
                await ctx.send(f"{action} is not a valid argument")

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the latency of the bot"""
        latency = round((self.client.latency * 1000), 2)
        await ctx.send(f"pong! Latency is {latency}ms")


def setup(client):
    client.add_cog(Development(client))
