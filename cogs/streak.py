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
        
        #Decode the arguments to get current starting date
        starting_date = datetime.utcnow() - timedelta(seconds=time)

        #Get user data on current streak
        rows = await database.select_relapse_data(ctx.author.id)

        #If previous streak
        if len(rows) > 0:
            await self.db_streak_update(ctx, id=ctx.author.id)
        #If no previous streak
        else:
            await self.db_streak_update(ctx, previous=False)

    async def db_streak_update(self, ctx, previous=True):
        #update last update
        await database.update_user_data(user_id=ctx.author.id)

        #if previous streak insert relapse data
        if previous:
            await database.insert_relapse(user_id=ctx.author.id, relapse_utc=starting_date)
        
        #update roles
        await self.update_role()
        #post message
        if previous:
            streak_string = await self.get_streak_string(time)
            await ctx.send(f"Your previous streak was {streak_string[0]} days, and {streak_string[1]} hours. \n Dont be dejected")
        else:
            await ctx.send("This is your first sreak on record, good luck")
    
    async def get_streak_string(self, seconds):
        days = seconds // 24*3600
        hours = seconds // 3600
        return [days, hours]
    
    async def update_role(self):
        pass