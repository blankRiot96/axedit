import inspect
import logging
import os
import subprocess
import sys
import traceback
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


stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(LOG_FILE_PATH)

stream_handler.setFormatter(CustomFormatter())

logging.basicConfig(
    format="%(asctime)s : [%(levelname)s] : %(filename)s:%(lineno)d : %(message)s",
    datefmt=LOGGING_DATE_FMT,
    level=logging.DEBUG,
    handlers=[stream_handler, file_handler],
)


def true_exit():
    logging.debug("EXIT CALLED")
    raise SystemExit


__builtins__["exit"] = true_exit


def detached_main() -> None:
    """This function invokes the actual editor in a separate process
    and exits the terminal!"""

    main_path = FILE_PATH.parent.parent / "main.py"
    command = [sys.executable, str(main_path.absolute()), "--debug"]

    subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )


def debug_main():
    """Runs the editor in debug mode"""
    clear_logs()

    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    import pygame

    if not hasattr(pygame, "IS_CE"):
        logging.critical("This editor requires Pygame-CE")
        raise ModuleNotFoundError("Pygame-CE is not being used")

    from axedit.core import Core

    core = Core()
    core.run()


def clear_logs():
    if LOG_FILE_PATH.exists():
        with open(LOG_FILE_PATH, "w") as f:
            f.write("")


def display_logs():
    with open(LOG_FILE_PATH) as f:
        print(f.read())


def potential_main():
    """What the editor is potentially supposed to be"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            debug_main()
        elif sys.argv[1] == "--logs":
            display_logs()
        else:
            logging.critical(f"Invalid command '{sys.argv[1]}'")
            raise SystemExit
        return
    detached_main()


def main():
    """Runs the editor in a safespot"""
    try:
        potential_main()
    except Exception:
        logging.error(traceback.format_exc())
