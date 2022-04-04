import utils
from main import database
from discord.ext import commands
from datetime import datetime, timedelta

class streak(commmands.Cog):

    def __init__(self):
        self.client = client
    
    @commands.command(name="relapse")
    @commands.check(utils.is_in_streak_channel)
    async def relapse(self, ctx,  *, time: utils.TimeConverter=None):
        
        starting_date = datetime.utcnow() - timedelta(seconds=time)
        rows = await database.select_relapse_data(ctx.author.id)

        #If they have a pervious streak

        if not len(rows):
            await database.userdata_insert_query()