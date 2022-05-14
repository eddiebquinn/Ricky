from discord.ext import commands, tasks#
from itertools import cycle

class Meta(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.status = cycle(["Hi, im ricky!"])
        self.activity_cycle.start()
        
    @tasks.loop(minutes=1)
    async def activity_cycle(self):
        await self.client.change_presence(
            status=discord.Status.online, activity=discord.Game(next(status))
            )

def setup(client):
    discord_conn.client.add_cog(Meta(client))