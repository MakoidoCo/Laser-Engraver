import logging
from colorlog import ColoredFormatter

FORMATTER = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s: %(message)s\n",
    datefmt="%Y-%m-%d %H:%M:%S",
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

HANDLER = logging.StreamHandler()
HANDLER.setFormatter(FORMATTER)

LOGLEVEL = logging.INFO

__all__ = ['FORMATTER', 'HANDLER', 'LOGLEVEL']