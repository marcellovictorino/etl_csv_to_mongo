import logging
import os
import sys
from dotenv import load_dotenv


# Read local hidden .env file, to access environment variables
load_dotenv()


def silent_remove_file(filepath: str) -> None:
    try:
        os.remove(filepath)
    except OSError:
        pass


def set_logger(logger_name: str) -> logging.getLogger:
    """Initializes logger with appropriate level and formatting"""

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
