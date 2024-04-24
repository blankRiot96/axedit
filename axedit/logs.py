import inspect
import logging
import sys
import warnings
from pathlib import Path

import colorama

FILE_PATH = Path(inspect.getfile(inspect.currentframe()))
LOG_FILE_PATH = FILE_PATH.parent.parent / "app.log"
WARN_FILE_PATH = FILE_PATH.parent.parent / "warns.log"
LOGGING_DATE_FMT = "%H:%M:%S"
WHITELISTED_LOGGERS = ["axedit"]
LOG_FORMAT = "[%(name)s](%(filename)s:%(lineno)d) %(message)s"

if len(sys.argv) > 1 and sys.argv[1] in ("--debug", "--hidden-debug"):
    warnings.simplefilter("always")

if len(sys.argv) > 2 and sys.argv[2] == "--warn":
    WHITELISTED_LOGGERS.append("py.warnings")


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


handlers = []

if len(sys.argv) > 1 and sys.argv[1] in ("--debug", "--hidden-debug"):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomFormatter())
    stream_handler.addFilter(axe_filter)
    handlers.append(stream_handler)

file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setFormatter(CustomFormatter())
file_handler.addFilter(axe_filter)
handlers.append(file_handler)


warn_file_handler = logging.FileHandler(WARN_FILE_PATH)
warn_file_handler.addFilter(lambda logger: logger.name == "py.warnings")
handlers.append(warn_file_handler)

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOGGING_DATE_FMT,
    level=logging.DEBUG,
    handlers=handlers,
)

# The main logger to use
logger = logging.getLogger("axedit")
logging.captureWarnings(True)
