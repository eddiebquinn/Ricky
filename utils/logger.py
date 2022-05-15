import logging
global LOGGER


def logger_init():
    global LOGGER
    log_format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(
        filename="ricky.log",
        format=log_format)
    LOGGER = logging.getLogger()
    LOGGER.warning(f"initilised logger with '{LOGGER.level}' logging level")
