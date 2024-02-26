import inspect
import logging
from pathlib import Path

import colorama

FILE_PATH = Path(inspect.getfile(inspect.currentframe()))
LOG_FILE_PATH = FILE_PATH.parent.parent / "app.log"
LOGGING_DATE_FMT = "%H:%M:%S"


class CustomFormatter(logging.Formatter):
    colored_format = "%(asctime)s : {color}[%(levelname)s]{reset} : %(filename)s:%(lineno)d : %(message)s"

    reset = colorama.Fore.RESET
    FORMATS = {
        logging.DEBUG: colored_format.format(color=colorama.Fore.GREEN, reset=reset),
        logging.INFO: colored_format.format(color=colorama.Fore.WHITE, reset=reset),
        logging.WARNING: colored_format.format(color=colorama.Fore.YELLOW, reset=reset),
        logging.ERROR: colored_format.format(color=colorama.Fore.RED, reset=reset),
        logging.CRITICAL: colored_format.format(
            color=colorama.Fore.MAGENTA, reset=reset
        ),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=LOGGING_DATE_FMT)
        return formatter.format(record)


# TODO: Disable all the loggers apart from "axedit", parso logs infiltrate otherwise
axe_filter = logging.Filter("axedit")

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(LOG_FILE_PATH)

stream_handler.setFormatter(CustomFormatter())
stream_handler.addFilter(axe_filter)
file_handler.addFilter(axe_filter)

logging.basicConfig(
    format="%(asctime)s : [%(levelname)s] : %(filename)s:%(lineno)d : %(message)s",
    datefmt=LOGGING_DATE_FMT,
    level=logging.DEBUG,
    handlers=[stream_handler, file_handler],
)

# The main logger to use
logger = logging.getLogger("axedit")
