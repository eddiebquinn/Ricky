import utils.logger as logger
import logging
import database
import discord_conn


def init():
    """ Launches the bot """
    logger.logger_init()
    database.database_init()
    discord_conn.launch_discord_bot()


if __name__ == "__main__":
    init()
