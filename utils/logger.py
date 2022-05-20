import logging
import sys
global LOGGER


def logger_init(level=logging.WARNING):
    """Initalises the logger"""
    global LOGGER
    log_format = "%(levelname)s %(asctime)s - %(message)s"

    logging.basicConfig(
        format=log_format,
        level=level,
        handlers=[
            logging.FileHandler("ricky.log"),
            logging.StreamHandler(sys.stdout)
        ])

    LOGGER = logging.getLogger()
    LOGGER.warning(f"initilised logger with '{LOGGER.level}' logging level")
