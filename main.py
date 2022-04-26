import utils
from databse import Database
import discord_conn

def init():
    """ Launches the bot """
    global database 
    database = Database(config=utils.extract_json()["sql_connection_settings"])
    discord_conn.launch_discord_bot()

if __name__ == "__main__":
    init()