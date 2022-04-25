import utils
from main import database
from discord.ext import commands
from datetime import datetime, timedelta

class streak(commmands.Cog):

    def __init__(self):
        self.client = client
    
    @commands.command(name="relapse")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 300, commands.BucketType.user)
    async def relapse(self, ctx,  *, time: utils.TimeConverter=None):
        
        #Decode the arguments to get current starting date
        starting_date = datetime.utcnow() - timedelta(seconds=time)

        #Get user data on current streak
        previous_streak_data = await database.select_relapse_data(ctx.author.id)

        #If previous streak
        previous = True if len(previous_streak_data) > 0  else False

        #update database
        await self.db_streak_update(ctx=ctx, previous=previous)

        #find current streak length
        previous_start_date = previous_streak_data[0][2]
        current_streak_length = (starting_date - previous_start_date).total_seconds()
        streak_string = await self.get_streak_string(current_streak_length)

        #update roles
        await self.update_role(ctx, streak_string[0])

        #post message
        if previous:
            await ctx.send(f"Your previous streak was {streak_string[0]} days, and {streak_string[1]} hours. \n Dont be dejected")
        else:
            await ctx.send("This is your first sreak on record, good luck")

    @commands.command(name="update")
    @commands.cooldown(3, 900, commands.BucketType.user)
    @commands.check(utils.is_in_streak_channel)
    async def update(self, ctx):

        #get streak str and post message
        previous_streak_data = await database.select_relapse_data(ctx.author.id)
        previous_start_date = previous_streak_data[0][2]
        current_streak_length = previous_start_date.total_seconds()
        streak_string = await self.get_streak_string(current_streak_length)
        await ctx.send(f"Your streak is {streak_string[0]} days, and f{streak_string[1]} hours long")

        #update roles
        await self.update_role(ctx, streak_string[0])

    async def db_streak_update(self, ctx, previous=True):
        #update last update
        await database.update_user_data(user_id=ctx.author.id)

        #if previous streak insert relapse data
        if previous:
            await database.insert_relapse(user_id=ctx.author.id, relapse_utc=starting_date)
    
    async def get_streak_string(self, seconds):
        days = seconds // 24*3600
        hours = seconds // 3600
        return [days, hours]
    
    async def calc_streak_length(self, previous_start_date, current_start_date):
        return (current_start_date - previous_start_date).total_seconds()
    
    async def update_role(self, ctx, days):

        ## loop through servers the user is in --> list of all servers user is in called used_servers
        gross_servers = self.client.guilds()
        used_servers = []
        for server in gross_servers:
            for member in server:
                if ctx.author == member:
                    used_servers.append(server)

        ## loop through used_servers to find the current role they have (if any) --> dict where key==guild value== role called owned_role

        owned_roles = {}
        for server in used_servers:

            guild_roles = await database.select_guild_roles(server.id)
            roles = []
            for role in guild_roles:
                roles.append(role[3])

            member = server.fetch_member(ctx.author.id)
            owwned_role = await self.get_owned_streak_roles(member, roles)
            owned_roles[server] = owwned_role
        
        ## loop through databse to find the correct role for the user, for servers he is is in --> dict where key == guild value == role called reserved_role
        
        deserved_roles = {}
        for server in used_servers:
            guild_roles = await database.select_guild_roles(server.id)
            deserved_role = await self.get_deserved_streak_role(days, guild_roles)
            deserved_roles[server] = deserved_role 

        ## for every server in used servers
        for server in used_servers:

            #if deserved = owned return
            if owned_roles[server] == deserved_roles[server]:
                return
            
            ## get author member object for server
            guild_member = await guild.fetch_member(ctx.author.id)

            ## if they have any role
            if owned_roles[server] != None:

                #remove role
                await guild_member.remove_roles(owned_roles[server], reason="updating streak roles")

            ## add desrved role
            await guild_member.add_roles(deserved_role[server], reason="updating streak roles")

            
    async def get_owned_streak_roles(self, member, guild_roles):
        for role in member.roles:
            if role.id in guild_roles:
                return role
        return None


    async def get_deserved_streak_role(self, days, guild_roles):
        role = []
        for role in guild_roles:
            if days < role[2]:
                roles.append(int(role[2]))
        min_val = min(role)
        min_val_index = role.index(min_val)
        return role[min_val_index]