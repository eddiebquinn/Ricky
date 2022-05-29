import utils.utils as utils
from utils.logger import LOGGER
import database
import discord_conn
import discord
from discord.ext import commands
from datetime import datetime, timedelta


class Streak(commands.Cog):

    def __init__(self, client):
        LOGGER.warning(f"initilised {__class__.__cog_name__} cog")
        self.client = client

    @commands.command(name="relapse")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 300, commands.BucketType.user)
    async def relapse(self, ctx,  *, declared_streak_length: utils.TimeConverter = 0.0):
        """Updated the users roles and databse entry with most recent relaspe, and posts message

        Args:
            declared_streak_length (utils.TimeConverter, optional): A series of time keys and coefficents (1d 2m 3h). Defaults to 0.0.
        """
        if declared_streak_length is False:
            return
        starting_date = datetime.utcnow() - timedelta(seconds=int(declared_streak_length))
        userdata = await database.DATABASE_CONN.seclect_user_data(ctx.author.id)
        previous = True if userdata else False
        if previous:
            relapse_data = await database.DATABASE_CONN.select_relapse_data(ctx.author.id)
            most_recent_relapse = relapse_data[0][2]
            previous_streak_length = starting_date - most_recent_relapse
            previous_streak_length = await self.get_streak_string(previous_streak_length.total_seconds())
        await self.db_streak_update(
            ctx=ctx,
            previous=previous,
            starting_date=starting_date)
        current_streak_length = datetime.utcnow() - starting_date
        current_streak_length = await self.get_streak_string(current_streak_length.total_seconds())
        await self.update_role(ctx, current_streak_length[0])
        if previous:
            await ctx.send(f"Your previous streak was {previous_streak_length[0]} days, and {previous_streak_length[1]} hours. \n Dont be dejected")
        else:
            await ctx.send("This is your first sreak on record, good luck")

    @commands.command(name="update")
    @commands.check(utils.is_in_streak_channel)
    @commands.cooldown(3, 900, commands.BucketType.user)
    async def update(self, ctx):
        """Updated the users roles and posts their current streak length"""
        userdata = await database.DATABASE_CONN.seclect_user_data(ctx.author.id)
        previous = True if userdata else False
        if not previous:
            await ctx.send("You dont appear to have any previous streaks on record. Please do `!relapse` to start your first one!")
            return
        previous_streak_data = await database.DATABASE_CONN.select_relapse_data(ctx.author.id)
        most_recent_relapse = previous_streak_data[0][2]
        current_streak_length = datetime.utcnow() - most_recent_relapse
        streak_string = await self.get_streak_string(current_streak_length.total_seconds())
        await ctx.send(f"Your streak is {streak_string[0]} days, and {streak_string[1]} hours long")
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

    async def update_role(self, ctx, current_streak_length):
        """Updates the users roles based on current streak length

        Args:
            current_streak_length (time delta): The total streak length in seconds
        """

        used_guilds = await self.get_used_guilds(author=ctx.author)
        owned_roles = await self.get_owned_roles(author=ctx.author, used_guilds=used_guilds)
        deserved_roles = await self.get_deserved_roles(used_guilds=used_guilds, current_streak_length=current_streak_length)

        for guild in used_guilds:
            if owned_roles[guild] == deserved_roles[guild]:
                continue

            guild_member = await guild.fetch_member(ctx.author.id)
            if owned_roles[guild] != None:
                await guild_member.remove_roles(owned_roles[guild], reason="updating streak roles")
            await guild_member.add_roles(deserved_roles[guild], reason="updating streak roles")

    async def get_used_guilds(self, author):
        """Gets the guilds of which the user is part, and has roles activated

        Args:
            author: The user who the guilds are being checked against

        Returns:
            list: The list of guilds which meet the conditions
        """
        gross_guilds = self.client.guilds
        used_guilds = []
        for guild in gross_guilds:
            guild_data = await database.DATABASE_CONN.select_guild_data(guild.id)
            for member in guild.members:
                if author.id == member.id:
                    if guild_data[3] == 1:
                        used_guilds.append(guild)
        return used_guilds

    async def get_owned_roles(self, author, used_guilds: list):
        """Gets the owned roles of the member in each guild

        Args:
            author: The user who the guilds are being checked against
            used_guilds (list): The guilds which both the user and bot are in, which have roles turned on

        Returns:
            dict: Dictionary the used servers, and the streak role the user has
        """
        owned_roles = {}
        for guild in used_guilds:
            guild_roles_raw = await database.DATABASE_CONN.select_guild_roles(guild.id)
            guild_roles = []
            for role in guild_roles_raw:
                guild_roles.append(role[3])
            member = await guild.fetch_member(author.id)
            owned_role = None
            for role in member.roles:
                if role.id in guild_roles:
                    owned_role = role
                    break
            owned_roles[guild] = owned_role
        return owned_roles

    async def get_deserved_roles(self, used_guilds: list, current_streak_length):
        """Gets the desrved roles of the member in each guild based on current streak length

        Args:
            used_guilds (list): The guilds which both the user and bot are in, which have roles turned on
            current_streak_length: The current length of the users streak

        Returns:
            _type_: _description_
        """
        deserved_roles = {}
        for guild in used_guilds:
            guild_streak_roles = await database.DATABASE_CONN.select_guild_roles(guild.id)
            deserved_role = None
            potential_roles = []
            for role in guild_streak_roles:
                if current_streak_length < role[2]:
                    potential_roles.append(int(role[2]))
            if len(potential_roles) > 0:
                min_val = min(potential_roles)
                min_val_index = potential_roles.index(min_val)
                deserved_role = guild_streak_roles[min_val_index][3]
            if deserved_role is not None:
                deserved_role = guild.get_role(deserved_role)
            deserved_roles[guild] = deserved_role
        return deserved_roles


def setup(client):
    discord_conn.client.add_cog(Streak(client))
