from discord.ext import commands
import random


class Motivation(commands.Cog):

    def __init__(self, client):
        print(f"initilised {__class__.__cog_name__} cog")
        self.client = client
        self.motivational_links = (
            "https://www.youtube.com/watch?v=xBvPPW5uYVQ",
            "https://cdn.shopify.com/s/files/1/0070/7032/files/Fearless_Motivational_Quote_Desktop_Wallpaper_1.png?format=jpg&quality=90&v=1600450412",
            "https://www.success.com/wp-content/uploads/legacy/sites/default/files/new2.jpg",
            "https://www.betterteam.com/images/betterteam-motivational-quotes-for-the-workplace-5355x3570-20201119.jpeg?crop=21:16,smart&width=420&dpr=2",
            "https://liveboldandbloom.com/wp-content/uploads/2022/01/3-10.png",
            "https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/inspirational-quotes-theodore-roosevelt-1562000239.png?crop=1xw:1xh;center,top&resize=480:*",
            "https://i.pinimg.com/originals/d1/c5/c9/d1c5c9eb72027fa0e62da31135578f9d.jpg",
            "https://img.theculturetrip.com/450x/smart/wp-content/uploads/2017/01/seek-respect-not-attention--it-lasts-longer--1.png",
            "https://www.ourmindfullife.com/wp-content/uploads/2020/07/inspiring-work-quotes-2.jpg",
        )

    @commands.command(name="motivate",  aliases=["m", "moti"])
    async def motivation(self, ctx):
        """Sends a motivational link"""
        link = random.choice(self.motivational_links)
        await ctx.send(link)


def setup(client):
    client.add_cog(Motivation(client))
