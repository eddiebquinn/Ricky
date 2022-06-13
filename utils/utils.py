import database
from discord.ext import commands
import json
import time
import asyncio
import re


class TimeConverter(commands.Converter):

    async def convert(self, ctx, arguments: str()):
        """Converts a string of time keys/coefficents and converts to seconds

        Args:
            arguments (str): A series of time keys and coefficents (1d 2m 3h)

        Returns:
            int: The total seconds coresponding the the inserted arguments
        """
        args = arguments.lower().split()
        overide = False
        if "--overide" in arguments or "-o" in arguments:
            overide = True
            try:
                args.remove("--overide")
            except ValueError:
                args.remove("-o")
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if "M" in arguments:
            await ctx.send("please use 'm' istead of 'M'")
            return (False, overide)

        time = 0
        message = f"You can only use seconds, minutes, hours, and days as time keys. \n e.g. - `1d 4h 5m` for 1d 4 hours and 5m"
        for arg in args:
            part = re.split('(\d+)', arg)
            if part[0] != "":
                await ctx.send(message)
                return (False, overide)
            part.pop(0)
            if part[1] not in list(time_dict.keys()):
                await ctx.send(message)
                return (False, overide)
            unit = time_dict[part[1]]
            time += unit * int(part[0])
        return (float(time), overide)


async def is_in_streak_channel(ctx):
    """Contextually establishes of a message was sent in a guilds streak channel

    Returns:
        bool: Returns True if the channel if the streak channel
    """
    guild_data = await database.DATABASE_CONN.select_guild_data(ctx.guild.id)
    if guild_data[1] != 1:
        return True
    return guild_data[2] == ctx.channel.id


async def is_developer(ctx):
    """Contextually returns if the message author is a developer or not"""
    userdata = await database.DATABASE_CONN.seclect_user_data(ctx.author.id)
    return userdata[2] == 1


def extract_json():
    """Extracts settings.json file into a dictionary

    Returns:
       dict : Dictonary based on the settings.json file
    """
    file_ = open("settings.json")
    return json.load(file_)
