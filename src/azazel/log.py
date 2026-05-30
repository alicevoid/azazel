"""
Logger

    Designed to Log the events of Azazel

"""

import os
import logging
from logging.handlers import RotatingFileHandler


def get_logger(name="azazel"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # terminal output
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)  # logging info and above only

        # file output - rotating (1MB cap w/ 3 backups)
        log_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "azazel")
        os.makedirs(log_dir, exist_ok=True)
        fh = RotatingFileHandler(
            os.path.join(log_dir, "azazel.log"), maxBytes=1_000_000, backupCount=3
        )
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)  # logging everything
        logger.addHandler(fh)

    return logger
