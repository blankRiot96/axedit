import inspect
import os
import subprocess
import sys
import traceback
from pathlib import Path

from logit import Level, log

FILE_PATH = Path(inspect.getfile(inspect.currentframe()))
LOG_FILE_PATH = FILE_PATH.parent.parent / "app.log"

if LOG_FILE_PATH.exists():
    os.remove(LOG_FILE_PATH)
log.config(log_file_path=LOG_FILE_PATH, level=Level.CLUTTER)


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
    from axedit.core import Core

    core = Core()
    core.run()


def potential_main():
    """What the editor is potentially supposed to be"""
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        debug_main()
        return

    detached_main()


def main():
    """Runs the editor in a safespot"""
    try:
        potential_main()
    except Exception:
        log.error(traceback.format_exc())
