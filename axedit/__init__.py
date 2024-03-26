import inspect
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import subprocess
import sys
import traceback
from pathlib import Path

from axedit.funcs import safe_close_connections
from axedit.logs import logger

FILE_PATH = Path(inspect.getfile(inspect.currentframe()))
LOG_FILE_PATH = FILE_PATH.parent.parent / "app.log"


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

    import pygame

    if not hasattr(pygame, "IS_CE"):
        logger.critical("This editor requires Pygame-CE")
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
            logger.critical(f"Invalid command '{sys.argv[1]}'")
            raise SystemExit
        return
    detached_main()


def main():
    """Runs the editor in a safespot"""
    try:
        potential_main()
    except (Exception, KeyboardInterrupt):
        logger.error(traceback.format_exc())
        safe_close_connections()
    finally:
        safe_close_connections()
