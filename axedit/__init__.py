import axedit.first_run  # isort: skip

import os
import subprocess
import sys
import traceback
from pathlib import Path

from axedit import shared
from axedit.funcs import safe_close_connections
from axedit.logs import logger

FOLDER_PATH = shared.AXE_FOLDER_PATH.parent
LOG_FILE_PATH = FOLDER_PATH / "app.log"
WARN_FILE_PATH = FOLDER_PATH / "warns.log"
PROFILE_FILE_PATH = FOLDER_PATH / "main.prof"


def detached_main() -> None:
    """This function invokes the actual editor in a separate process
    and exits the terminal!"""

    main_path = FOLDER_PATH / "main.py"
    command = [sys.executable, str(main_path.absolute()), "--hidden-debug"]

    if "--profile" in sys.argv:
        command.append("--profile")

    subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
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

    if WARN_FILE_PATH.exists():
        with open(WARN_FILE_PATH, "w") as f:
            f.write("")


def display_logs():
    with open(LOG_FILE_PATH) as f:
        print(f.read())


def display_profile():
    try:
        subprocess.run(
            [sys.executable, "-m", "snakeviz", PROFILE_FILE_PATH.absolute().__str__()]
        )
    except KeyboardInterrupt:
        return


def potential_main():
    """What the editor is potentially supposed to be"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--debug", "--hidden-debug"):
            debug_main()
        elif sys.argv[1] == "--logs":
            display_logs()
        elif sys.argv[1] == "--profile":
            detached_main()
        elif sys.argv[1] == "--snakeviz":
            display_profile()
        else:
            logger.critical(f"Invalid command '{sys.argv[1]}'")
            raise SystemExit
        return

    detached_main()


def _main():
    """Runs the editor in a safespot"""
    try:
        potential_main()
    except (Exception, KeyboardInterrupt):
        logger.error(traceback.format_exc())
    except SystemExit:
        pass
    finally:
        safe_close_connections()


def main():
    profiling = "--profile" in sys.argv
    debugging = "--debug" in sys.argv or "--hidden-debug" in sys.argv
    if profiling and debugging:
        main_path = shared.AXE_FOLDER_PATH.parent / "main.py"
        os.system(
            f"{sys.executable} -m cProfile -o '{PROFILE_FILE_PATH.absolute()}' '{main_path.absolute()}' --debug"
        )
    else:
        _main()
