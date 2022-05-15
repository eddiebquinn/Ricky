import discord_conn
import utils.utils as utils
import utils.logger as logger
import database


def init():
    """ Launches the bot """
    logger.logger_init()
    database.database_init(echo=True)
    discord_conn.launch_discord_bot()


if __name__ == "__main__":
    init()
