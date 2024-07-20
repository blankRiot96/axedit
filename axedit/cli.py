import typing as t
from pathlib import Path

import click

from axedit.internals import Internals
from axedit.window import Window


@click.command(name="", help="Axedit: Modal Text Editor")
@click.argument("path", default=".", required=False)
def run(path: str) -> t.NoReturn:
    """Runs Axedit"""

    path = Path(path)
    Internals.register_path_selection(path)

    window = Window()
    window.run()
