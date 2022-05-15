import utils
import database
import discord_conn
import discord
from discord.ext import commands
from datetime import datetime, timedelta


class Streak(commands.Cog):

    def __init__(self, client):
        print(f"initilised {__class__.__cog_name__} cog")
        self.client = client

    @commands.command(name="relapse")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 300, commands.BucketType.user)
    async def relapse(self, ctx,  *, declared_streak_length: utils.TimeConverter = 0.0):
        """Updated the users roles and databse entry with most recent relaspe, and posts message

        Args:
            declared_streak_length (utils.TimeConverter, optional): A series of time keys and coefficents (1d 2m 3h). Defaults to 0.0.
        """
        # Decode the arguments to get current starting date
        if declared_streak_length is False:
            return
        starting_date = datetime.utcnow() - timedelta(seconds=int(declared_streak_length))

        # Previous streak data
        userdata = await database.DATABASE_CONN.seclect_user_data(ctx.author.id)
        previous = True if userdata else False

        # Get user data on current streak
        if previous:
            relapse_data = await database.DATABASE_CONN.select_relapse_data(ctx.author.id)
            most_recent_relapse = relapse_data[0][2]
            previous_streak_length = starting_date - most_recent_relapse
            previous_streak_length = await self.get_streak_string(previous_streak_length.seconds)

        # update database
        await self.db_streak_update(
            ctx=ctx,
            previous=previous,
            starting_date=starting_date)

        # update roles
        current_streak_length = datetime.utcnow() - starting_date
        current_streak_length = await self.get_streak_string(current_streak_length.seconds)
        await self.update_role(ctx, current_streak_length[0])

        # post message
        if previous:
            await ctx.send(f"Your previous streak was {previous_streak_length[0]} days, and {previous_streak_length[1]} hours. \n Dont be dejected")
        else:
            await ctx.send("This is your first sreak on record, good luck")

    @commands.command(name="update")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 900, commands.BucketType.user)
    async def update(self, ctx):
        """Updated the users roles and posts their current streak length"""
        # Previous streak data
        userdata = await database.DATABASE_CONN.seclect_user_data(ctx.author.id)
        previous = True if userdata else False

        # If they dont have a previous streak
        if not previous:
            await ctx.send("You dont appear to have any previous streaks on record. Please do `!relapse` to start your first one!")
            return

        # get streak str and post message
        previous_streak_data = await database.DATABASE_CONN.select_relapse_data(ctx.author.id)
        most_recent_relapse = previous_streak_data[0][2]
        current_streak_length = datetime.utcnow() - most_recent_relapse
        streak_string = await self.get_streak_string(current_streak_length.total_seconds())
        await ctx.send(f"Your streak is {streak_string[0]} days, and {streak_string[1]} hours long")

        # update roles
        await self.update_role(ctx, streak_string[0])

    async def db_streak_update(self, ctx, previous: bool, starting_date):
        """Adds/updates the users most recent update in user table

        Args:
            previous (bool): Weather the user has a previous streak on record
            starting_date (timedelta): The length of the streak
        """
        if previous:
            await database.DATABASE_CONN.update_user_data(ctx.author.id)
        else:
            await database.DATABASE_CONN.insert_user_data(ctx.author.id)

        # if previous streak insert relapse data
        await database.DATABASE_CONN.insert_relapse(user_id=ctx.author.id, relapse_utc=starting_date)

    async def get_streak_string(self, seconds: int):
        """Converts seconds into a tuple of days and hours

        Args:
            seconds (int): The seconds to be converted

        Returns:
            list: A list comprised of [days, hours] where items are intergers
        """
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return [int(days), int(hours)]

    async def calc_streak_length(self, previous_start_date, current_start_date):
        """Returns streak length based on two imputs

        Args:
            previous_start_date (timedate): The previous relapse date
            current_start_date (timedate): The current start date

        Returns:
            timedelta: The current streak length
        """
        return (current_start_date - previous_start_date).total_seconds()

    async def update_role(self, ctx, current_streak_length):
        """Updates the users roles based on current streak length

        Args:
            current_streak_length (time delta): The total streak length in seconds
        """
        guild_streak_roles = await database.DATABASE_CONN.select_guild_roles(guild.id)

        used_guilds = await self.get_used_guilds(author=ctx.author)
        owned_roles = await self.get_owned_roles(
            author=ctx.author,
            used_guilds=used_guilds,
            guild_streak_roles=guild_streak_roles)
        deserved_roles = await self.get_deserved_roles(
            used_guilds=used_guilds,
            current_streak_length=current_streak_length,
            guild_streak_roles=guild_streak_roles)

        for guild in used_guilds:
            if owned_roles[guild] == deserved_roles[guild]:
                continue

            guild_member = await guild.fetch_member(ctx.author.id)
            if owned_roles[guild] != None:
                await guild_member.remove_roles(owned_roles[guild], reason="updating streak roles")
            await guild_member.add_roles(deserved_roles[guild], reason="updating streak roles")

    async def get_used_guilds(self, author):
        gross_guilds = self.client.guilds
        used_guilds = []
        for guild in gross_guilds:
            for member in guild.members:
                if author.id == member.id:
                    used_guilds.append(guild)
        return used_guilds

    async def get_owned_roles(self, author, used_guilds, guild_streak_roles):
        owned_roles = {}
        for guild in used_guilds:
            roles = []
            for role in guild_streak_roles:
                roles.append(role[3])

            member = await guild.fetch_member(author.id)
            role = await self.get_owned_streak_roles(member, roles)
            if role is not None:
                role = guild.get_role(role)
            owned_roles[guild] = role
        return owned_roles

    async def get_deserved_roles(self, used_guilds, current_streak_length, guild_streak_roles):
        deserved_roles = {}
        for guild in used_guilds:
            role = await self.get_deserved_streak_role(current_streak_length, guild_streak_roles)
            if role is not None:
                role = guild.get_role(role)
            deserved_roles[guild] = role
        return deserved_roles

    async def get_owned_streak_roles(self, member: discord.Member, guild_roles):
        """Returns the roles the user currently has 

        Args:
            member (discord.Member): The user of the server being checked
            guild_roles (list): A list of server roles

        Returns:
            discord.Role: The role the user has
        """
        for role in member.roles:
            if role.id in guild_roles:
                return role
        return None

    async def get_deserved_streak_role(self, days, guild_roles):
        """Returns the role the user deserves

        Args:
            days (timedelta): The current streak length
            guild_roles (list): List of the streak roles the guild has

        Returns:
            discord.Role: The discord role the user deserves based on their streak length
        """
        roles = []
        for role in guild_roles:
            if days < role[2]:
                roles.append(int(role[2]))
        if len(role) > 0:
            min_val = min(roles)
            min_val_index = roles.index(min_val)
            return guild_roles[min_val_index][3]
        return None


def setup(client):
    discord_conn.client.add_cog(Streak(client))
