import inspect
import subprocess
import sys
from pathlib import Path


# This function invokes the actual editor in a separate process
# and exits the terminal!
def main():
    file_path = Path(inspect.getfile(inspect.currentframe()))
    main_path = file_path.parent.parent / "main.py"
    command = [sys.executable, str(main_path.absolute())]
    subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )
