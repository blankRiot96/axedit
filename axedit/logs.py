import inspect
import logging
from pathlib import Path

import colorama

FILE_PATH = Path(inspect.getfile(inspect.currentframe()))
LOG_FILE_PATH = FILE_PATH.parent.parent / "app.log"
LOGGING_DATE_FMT = "%H:%M:%S"
WHITELISTED_LOGGERS = ("axedit", "py.warnings")
LOG_FORMAT = "[%(name)s](%(filename)s:%(lineno)d) %(message)s"


class CustomFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: colorama.Fore.GREEN,
        logging.INFO: colorama.Fore.WHITE,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelno)
        reset = colorama.Fore.RESET
        log_fmt = LOG_FORMAT.replace("%(name)s", f"{log_color}%(name)s{reset}")
        log_fmt = log_fmt.replace(
            "%(filename)s:%(lineno)d",
            f"{colorama.Fore.RED}%(filename)s:%(lineno)d{colorama.Fore.RESET}",
        )
        formatter = logging.Formatter(log_fmt, datefmt=LOGGING_DATE_FMT)
        return formatter.format(record)


def axe_filter(logger: logging.Logger) -> bool:
    return logger.name in WHITELISTED_LOGGERS


stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(LOG_FILE_PATH)

stream_handler.setFormatter(CustomFormatter())
file_handler.setFormatter(CustomFormatter())

stream_handler.addFilter(axe_filter)
file_handler.addFilter(axe_filter)

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOGGING_DATE_FMT,
    level=logging.DEBUG,
    handlers=[stream_handler, file_handler],
)

# The main logger to use
logger = logging.getLogger("axedit")
logging.captureWarnings(True)
