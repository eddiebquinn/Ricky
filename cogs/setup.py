import discord
from discord.ext import commands
from discord.ext.commands import Cog
import database
from utils.logger import LOGGER


class Setup(commands.Cog):
    def __init__(self, client):
        LOGGER.warning(f"initialised {__class__.__cog_name__} cog")
        self.client = client
        self.user = self.client.user
        self.link = "https://github.com/eddiebquinn/Ricky/wiki/Guild-configuration-for-admins-moderators"

        self.streak_roles = (
            ((130, 81, 245), "3rd year +", 1460),
            ((0, 118, 255), "2nd year", 730),
            ((2, 248, 255), "6th - 12th month", 365),
            ((0, 250, 175), "3rd-5th month", 150),
            ((8, 238, 0), "2nd month", 60),
            ((169, 255, 0), "3rd - 4th week", 30),
            ((255, 255, 0), "2nd week", 14),
            ((255, 165, 0), "4th - 7th day", 7),
            ((245, 80, 0), "2nd - 3rd day", 3),
            ((255, 0, 0), "1st day", 1)
        )

    @Cog.listener()
    async def on_guild_join(self, guild):
        """Listener that activates when the bot is added to a new guild and adds guild to database"""
        LOGGER.info(f"bot added to {guild.id}")
        general_channel = False
        for channel in guild.text_channels:
            if channel.name.lower() == "general":
                general_channel = channel
        try:
            await guild.owner.send(f"Hi, im {self.user.name}, please check out {self.link} for instructions on how to configure me")
        except discord.errors.Forbidden:
            if general_channel:
                await general_channel.send(f"Hi, im {self.user.name}, please check out {self.link} for instructions on how to configure me")
        await database.DATABASE_CONN.insert_guild_data(guild.id)

    @commands.command(name="guild_info", aliases=["server_info"])
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def guild_info(self, ctx):
        """Sends general guild information and current bot settings"""
        guild_info = await database.DATABASE_CONN.select_guild_data(guild_id=ctx.guild.id)

        embed = discord.Embed(
            title="Guild Info",
            url=self.link,
            description="General guild information and current bot settings",
            color=0x02f8ff)
        embed.set_author(
            name=self.user.name,
            url="https://github.com/eddiebquinn/Ricky",
            icon_url=self.user.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Guild name", value=ctx.guild.name, inline=False)
        embed.add_field(
            name="Owner", value=ctx.guild.owner.mention, inline=False)
        embed.add_field(name="Population",
                        value=ctx.guild.member_count, inline=False)
        embed.add_field(name="Creation date",
                        value=ctx.guild.created_at.date(), inline=False)
        embed.add_field(name="Streak Channel Limit",
                        value=guild_info[1], inline=False)
        embed.add_field(name="Streak Channel",
                        value=guild_info[2], inline=False)
        embed.add_field(name="Roles enabled",
                        value=guild_info[3], inline=False)
        embed.set_footer(
            text="Ricky Bot is an open source addiction recovery tool, coded in Python. To get involved visit the github")
        await ctx.send(embed=embed)

    @commands.command(name="setup_guild")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def setup_guild(self, ctx):
        """Adds the guild to the database, in case the bot failed to do so automatically"""
        guild_data = await database.DATABASE_CONN.select_guild_data(ctx.guild.id)
        if guild_data is not None:
            if len(guild_data) > 0:
                await ctx.send(f"Data for {ctx.guild.name}  is already in the database")
                return
        await database.DATABASE_CONN.insert_guild_data(ctx.guild.id)
        await ctx.send(f"Data for {ctx.guild.name} inserted into database")

    @commands.command(name="toggle")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(3, 300, commands.BucketType.user)
    async def toggle_db_settings(self, ctx, raw_setting=None):
        """Used to toggle database settings related to the guild table

        Args:
            raw_setting (str): You can choose either `channel_limit` or `streak_roles`
        """

        settings = {"channel_limit": "streak_channel_limit",
                    "streak_roles": "roles_enabled"}
        if raw_setting not in settings.keys():
            await ctx.send("please toggle a valid setting")
            return

        data = await database.DATABASE_CONN.select_guild_data(ctx.guild.id)
        column_map = {"streak_channel_limit": 1, "roles_enabled": 3}
        value = data[column_map[settings[raw_setting]]]
        if value == 0:
            new_val = 1
        if value == 1:
            new_val = 0

        data = await database.DATABASE_CONN.update_guild_data(ctx.guild.id, {settings[raw_setting]: new_val})
        if data:
            await ctx.send(f"Successfully updated {raw_setting}")

    @commands.command(name="setup_streak_channel")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(3, 300, commands.BucketType.user)
    async def setup_streak_channel(self, ctx):
        """Chnages the streak channel to the channel command is sent it"""
        data = await database.DATABASE_CONN.update_guild_data(ctx.guild.id, {"streak_roles_channel": ctx.channel.id})
        if data:
            await ctx.send(f"Successfully updated streak channel to {ctx.channel.name}")

    @commands.command(name="Setup_roles")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def build_roles(self, ctx, *args):
        """Crates default roles and adds them to the database

        Args:
            args (str): You can choose either `overide` or `hoist`.
                Overide deleted old roles and makes new ones
                Hoist makes it so the roles are displayed separately to others
        """
        overide = False
        hoist = False
        for arg in args:
            arg.lower()
            hoist = True if arg == "hoist" else False
            overide = True if arg == "overide" else False
            if arg == "hoist" or "overide":
                continue
            else:
                await ctx.send(f"{arg} is not a valid argument")
                return

        roles = await database.DATABASE_CONN.select_guild_roles(ctx.guild.id)
        if len(roles) > 0:
            if not overide:
                await ctx.send("There are already roles configured for this server, are you sure you want to do this?")
                await ctx.send("If you are you sure want to do this type in `!setup_roles overide`")
                return
            if overide:
                await self.do_overide(ctx.guild, roles)

        await ctx.send("setting up roles, this may take some time")
        response = await self.create_roles(guild=ctx.guild, hoist=hoist)
        if response is False:
            await ctx.send("Role creation failed")
            return
        response = await self.roles_into_database(guild=ctx.guild, roles=response)
        if response is True:
            await ctx.send("Role creation successful")

    async def do_overide(self, guild: discord.Guild, roles: list):
        """Deleted old roles and associated database entries

        Args:
            guild (discord.Guild): The guild of which the roles are being reset for
            roles (list): The list of roles to be reset
        """
        for role in roles:
            guild_role = guild.get_role(role[3])
            try:
                await guild_role.delete(reason=f"Deleted by {self.user.name} due to overide")
            except AttributeError:
                pass
            await database.DATABASE_CONN.delete_guild_roles(role[0])

    async def create_roles(self, guild: discord.Guild, hoist: bool = False):
        """Creates the standard discord recovery roles

        Args:
            guild (discord.Guild): The guild of which the roles are being made for
            hoist (bool, optional): Weather the roles should be displayed separately. Defaults to False.

        Returns:
            list: List of created roles
        """
        spawned_roles = []
        for role in self.streak_roles:
            rgb = role[0]
            colour = discord.Color.from_rgb(rgb[0], rgb[1], rgb[2])
            try:
                new_role = await guild.create_role(
                    name=role[1], colour=colour, reason=f"Auto generated by {self.user.name}")
                spawned_roles.append((role[2], new_role))
            except discord.Forbidden:
                await ctx.send("I do not have permission to create roles in this server")
                return False

        return spawned_roles

    async def roles_into_database(self, guild: discord.Guild, roles: list):
        """Inserts a series of roles into the database

        Args:
            guild (discord.Guild): The associated guild to the roles being added
            roles (list): The roles whose data is subject to being inserted into the database

        Returns:
            Bool: Returns True if data is successfully inserted into database
        """
        for role in roles:
            await database.DATABASE_CONN.insert_guild_roles(
                guild_id=guild.id,
                day_reach=role[0],
                role_id=role[1].id)
        return True


def setup(client):
    client.add_cog(Setup(client))
