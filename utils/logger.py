import logging
import sys
global LOGGER


def logger_init():
    global LOGGER
    log_format = "%(levelname)s %(asctime)s - %(message)s"

    logging.basicConfig(
        format=log_format,
        level=logging.WARNING,
        handlers=[
            logging.FileHandler("ricky.log"),
            logging.StreamHandler(sys.stdout)
        ])

    LOGGER = logging.getLogger()
    LOGGER.warning(f"initilised logger with '{LOGGER.level}' logging level")
