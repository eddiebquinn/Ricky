from databse import Database
from utils import extract_json

def init():
    """ Launches the bot """
    Database(config=extract_json()["sql_connection_settings"])

if __name__ == "__main__":
    init()