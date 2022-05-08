import utils
import database
import discord_conn
from discord.ext import commands
from datetime import datetime, timedelta

class streak(commands.Cog):

    def __init__(self, client):
        print("initilised streak cog")
        self.client = client

    @commands.command(name="relapse")
    @commands.cooldown(3, 300, commands.BucketType.user)
    async def relapse(self, ctx,  *, declared_streak_length:utils.TimeConverter=0.0):

        #Make sure its in the streak channel (this isnt the right way to do it, ill figure out the right way at a later date)
        guild_data = await database.database_conn.select_guild_data(ctx.guild.id)
        if guild_data[0][1]:
            if guild_data[0][2] != ctx.channel.id:
                return

        #Decode the arguments to get current starting date
        starting_date = datetime.utcnow() - timedelta(seconds=int(declared_streak_length))

        ## Previous streak data
        userdata = await database.database_conn.seclect_user_data(ctx.author.id)
        previous = True if userdata else False

        #Get user data on current streak
        if previous:
            relapse_data = await database.database_conn.select_relapse_data(ctx.author.id)
            most_recent_relapse = relapse_data[0][2]
            previous_streak_length = starting_date - most_recent_relapse
            previous_streak_length = await self.get_streak_string(previous_streak_length.seconds)

        #update database
        await self.db_streak_update(
            ctx=ctx,
            previous=previous,
            starting_date=starting_date)

        #update roles
        current_streak_length =  datetime.utcnow() - starting_date
        current_streak_length = await self.get_streak_string(current_streak_length.seconds)
        await self.update_role(ctx, current_streak_length[0])

        #post message
        if previous:
            await ctx.send(f"Your previous streak was {previous_streak_length[0]} days, and {previous_streak_length[1]} hours. \n Dont be dejected")
        else:
            await ctx.send("This is your first sreak on record, good luck")

    @commands.command(name="update")
    @commands.cooldown(3, 900, commands.BucketType.user)
    async def update(self, ctx):

        #Make sure its in the streak channel (this isnt the right way to do it, ill figure out the right way at a later date)
        guild_data = await database.database_conn.select_guild_data(ctx.guild.id)
        if guild_data[0][1]:
            if guild_data[0][2] != ctx.channel.id:
                return
        
        ## Previous streak data
        userdata = await database.database_conn.seclect_user_data(ctx.author.id)
        previous = True if userdata else False

        ## If they dont have a previous streak
        if not previous:
            await ctx.send("You dont appear to have any previous streaks on record. Please do `!relapse` to start your first one!")
            return

        #get streak str and post message
        previous_streak_data = await database.database_conn.select_relapse_data(ctx.author.id)
        most_recent_relapse = previous_streak_data[0][2]
        current_streak_length = datetime.utcnow() - most_recent_relapse
        streak_string = await self.get_streak_string(current_streak_length.seconds)
        await ctx.send(f"Your streak is {streak_string[0]} days, and {streak_string[1]} hours long")

        #update roles
        await self.update_role(ctx, streak_string[0])

    async def db_streak_update(self, ctx, previous, starting_date):
        if previous:
            await database.database_conn.update_user_data(ctx.author.id)
        else:
            await database.database_conn.insert_user_data(ctx.author.id)

        #if previous streak insert relapse data
        await database.database_conn.insert_relapse(user_id=ctx.author.id, relapse_utc=starting_date)

    async def get_streak_string(self, seconds):
        days = seconds // 86400
        hours = seconds // 3600
        return [days, hours]

    async def calc_streak_length(self, previous_start_date, current_start_date):
        return (current_start_date - previous_start_date).total_seconds()

    async def update_role(self, ctx, current_streak_length):

        ## loop through servers the user is in --> list of all servers user is in called used_servers
        gross_servers = self.client.guilds
        used_servers = []
        for server in gross_servers:
            for member in server.members:
                if ctx.author == member:
                    used_servers.append(server)

        ## loop through used_servers to find the current role they have (if any) --> dict where key==guild value== role called owned_role

        owned_roles = {}
        for server in used_servers:

            guild_roles = await database.database_conn.select_guild_roles(server.id)
            roles = []
            for role in guild_roles:
                roles.append(role[3])

            member = await server.fetch_member(ctx.author.id)
            owned_role = await self.get_owned_streak_roles(member, roles)
            owned_roles[server] = owned_role

        ## loop through database to find the correct role for the user, for servers he is is in --> dict where key == guild value == role called reserved_role

        deserved_roles = {}
        for server in used_servers:
            guild_roles = await database.database_conn.select_guild_roles(server.id)
            deserved_role = await self.get_deserved_streak_role(current_streak_length, guild_roles)
            deserved_roles[server] = deserved_role

        ## for every server in used servers
        for server in used_servers:

            #if deserved = owned return
            if owned_roles[server] == deserved_roles[server]:
                continue

            ## get author member object for server
            guild_member = await server.fetch_member(ctx.author.id)

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
        if len(role) > 0:
            min_val = min(role)
            min_val_index = role.index(min_val)
            return role[min_val_index]
        return None

def setup(client):
    discord_conn.client.add_cog(streak(client))
