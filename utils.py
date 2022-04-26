import main
from discord.ext import commands
import json
import time

class TimeConverter(commands.Converter):

    async def convert(self, ctx, argument):

        time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
        time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

        args = argument.lower()
        matches = re.findall(time_regex, args)
        time_ = 0
        for v, k in matches:
            try:
                time_ += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(
                    "{} is an invalid time-key! h/m/s/d are valid!".format(k)
                )
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time_
    
def extract_json():
    file_ = open("settings.json")
    return json.load(file_)

def is_in_streak_channel(guild_id:int, channel_id:int):
    data = main.database.select_guild_data(guild_id)[0]
    if data[1] != 1:
        return True
    return data[2] == channel_id