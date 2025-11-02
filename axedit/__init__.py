import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import argparse
import subprocess
import sys
import time
import traceback
from datetime import datetime

from axedit import shared
from axedit.logs import LOG_FILE_PATH, WARN_FILE_PATH, logger

FOLDER_PATH = shared.AXE_FOLDER_PATH


def spawn_detached_process() -> None:
    main_path = FOLDER_PATH / "__main__.py"
    command = [sys.executable, str(main_path.absolute()), "--direct"]

    subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _log_time_separator():
    now = datetime.now()
    tz_name = time.tzname[time.localtime().tm_isdst]  # gets abbreviation like IST
    formatted = now.strftime(f"%H:%M:%S {tz_name} %d/%m/%Y")
    logger.info(f"\n\nEditor launched at: {formatted}\n")


def launch_editor():
    _log_time_separator()

    import pygame

    if not hasattr(pygame, "IS_CE"):
        logger.critical("This editor requires Pygame-CE")
        raise ModuleNotFoundError("Pygame-CE is not being used")

    from axedit.config_manager import apply_config, create_config_file

    create_config_file()
    apply_config()

    from axedit.core import Core

    try:
        core = Core()
        core.run()
    except Exception:
        logger.critical(traceback.format_exc())


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


def main():
    parser = argparse.ArgumentParser(
        prog="axedit", description="modal text editor for Python"
    )
    parser.add_argument(
        "--direct", "-d", action="store_true", help="run editor directly"
    )
    parser.add_argument(
        "--read-logs",
        action="store_true",
        help="read axedit logs (crash reports, useful for debugging)",
    )

    args = parser.parse_args()
    if args.direct:
        launch_editor()
    elif args.read_logs:
        display_logs()
    else:
        spawn_detached_process()
