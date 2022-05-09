import database
from discord.ext import commands
import json
import time
import asyncio
import re

class TimeConverter(commands.Converter):

    async def convert(self, ctx, arguments):
        time_dict = {"s":1, "m":60, "h":3600, "d":86400}
        if "M" in arguments:
            await ctx.send("please use 'm' istead of 'M'")
            return False
        args = arguments.lower().split()
        time = 0
        message = f"You can only use seconds, minutes, hours, and days as time keys."
        for arg in args:
            part = re.split('(\d+)',arg)
            if part[0] != "":
                await ctx.send(message)
                return False
            part.pop(0)
            if part[1] not in list(time_dict.keys()):
                await ctx.send(message)
                return False
            unit = time_dict[part[1]]
            time += unit * int(part[0])
        return time

async def is_in_streak_channel(ctx):
    guild_data = await database.database_conn.select_guild_data(ctx.guild.id)
    if guild_data[1] != 1:
        return True
    return guild_data[2] == ctx.channel.id

def extract_json():
    file_ = open("settings.json")
    return json.load(file_)
