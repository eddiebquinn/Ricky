from discord.ext import commands

class Development(commands.Cog):
    def __init__(self, client):
        print(f"initilised {__class__.__cog_name__} cog")
        self.client = client

    @commands.command(name="cog", aliases=["cogs"])
    async def cog(self, ctx, action, *args):
        """Command to manually toggle cogs. For action use either\n**load** - load the cog\n**unload** - unload the cog\n**reload** - reload the cog"""
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
        await ctx.send(f"pong! Latency is {self.client.latency * 1000}ms")


def setup(client):
    client.add_cog(Development(client))
