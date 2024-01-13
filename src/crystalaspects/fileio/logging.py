import logging


def setup_logging(basic="DEBUG", console="INFO"):
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(level=basic)
    # Setting matplotlib logger to warning
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler("report.log", mode="w")
    file_handler.setLevel(basic)
    file_formatter = logging.Formatter(
       fmt="%(asctime)s-%(name)s-%(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Create a console handler to write logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console)
    console_formatter = logging.Formatter(
        "%(name)s-%(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # Get the root logger and add both the file and console handlers to it

    # logger.addHandler(file_handler)
    logger.addHandler(console_handler)
