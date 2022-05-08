import database
from discord.ext import commands
import json
import time
import asyncio
import re

class TimeConverter(commands.Converter):

    async def convert(self, ctx, argument):

        time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
        time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
        args = argument.lower()
        matches = re.findall(time_regex, args)
        if len(matches) < 1:
            await ctx.send("Invalid time-key! h/m/s/d are valid!")
            return None
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                message = f"{k} is an invalid time-key! h/m/s/d are valid!"
                raise commands.BadArgument(message)
                return None
            except ValueError:
                message = f"{v} is not a number"
                raise commands.BadArgument(v)
                return None
        return time

def extract_json():
    file_ = open("settings.json")
    return json.load(file_)
