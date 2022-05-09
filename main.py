import utils
import database
import discord_conn

global database_conn

def init():
    """ Launches the bot """
    database.database_init(echo=True)
    discord_conn.launch_discord_bot()

if __name__ == "__main__":
    init()
