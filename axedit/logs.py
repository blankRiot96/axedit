import logging
import warnings
from pathlib import Path

import colorama
from platformdirs import user_log_dir

log_dir = Path(user_log_dir("axedit"))
log_dir.mkdir(parents=True, exist_ok=True)

LOG_FILE_PATH = log_dir / "app.log"
WARN_FILE_PATH = log_dir / "warns.log"
LOGGING_DATE_FMT = "%H:%M:%S"
WHITELISTED_LOGGERS = ["axedit"]
LOG_FORMAT = "[%(name)s](%(filename)s:%(lineno)d) %(message)s"

warnings.simplefilter("always")


class CustomFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: colorama.Fore.WHITE,
        logging.INFO: colorama.Fore.GREEN,
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


def axe_filter(logger: logging.LogRecord) -> bool:
    return logger.name in WHITELISTED_LOGGERS


handlers = []

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

logger = logging.getLogger("axedit")
logging.captureWarnings(True)
