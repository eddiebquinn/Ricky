from databse import Database
from discord_connect import launch_discord_bot
from utils import extract_json

def init():
    """ Launches the bot """
    database = Database(config=extract_json()["sql_connection_settings"])
    launch_discord_bot()

if __name__ == "__main__":
    init()