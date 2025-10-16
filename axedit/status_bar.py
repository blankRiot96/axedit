import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pygame

from axedit import shared
from axedit.cmd_bar import CommandBar
from axedit.logs import logger
from axedit.state_enums import FileState
from axedit.utils import render_at


def get_environment_python_path() -> Path:
    unix_python = shutil.which("python")
    windows_python = shutil.which("py")

    if unix_python is not None:
        return Path(unix_python)
    elif windows_python is not None:
        return Path(windows_python)

    raise FileNotFoundError("No Python found in the environment!")


def get_version():
    src = textwrap.dedent("""
    import sys
    V = sys.version_info.major, sys.version_info.minor, sys.version_info.micro
    VERSION_STR = ".".join(map(str, V))
    print(VERSION_STR)
    """)

    return subprocess.check_output(
        [get_environment_python_path(), "-c", src], text=True
    ).strip()


VERSION_STR = get_version()


def is_venv():
    return bool(os.getenv("VIRTUAL_ENV"))


VENV_STR = "(venv) " if is_venv() else ""


class StatusBar:
    """
    file_name -> None
    loc -> shared.cursor_pos
    mode -> shared.mode
    """

    def __init__(self) -> None:
        self.status_str = "FILE: {file_name}{saved} | MODE: {mode} | LOC: {loc}"
        self.gen_surf()
        self.cmd = CommandBar()
        shared.typing_cmd = False
        self.jargon = ""
        self.command_bar = CommandBar()
        self.color = pygame.Color(shared.theme["light-bg"])

    def render_polygon(self, out_str: str, extra_len: int, color):
        angle_offset = 20
        poly_botleft = shared.FONT_WIDTH * len(out_str), shared.FONT_HEIGHT
        poly_topleft = poly_botleft[0] + angle_offset, 0
        poly_topright = (
            poly_topleft[0] + (extra_len * shared.FONT_WIDTH),
            0,
        )
        poly_botright = poly_topright[0] - angle_offset, shared.FONT_HEIGHT

        points = [poly_botleft, poly_topleft, poly_topright, poly_botright]
        pygame.draw.polygon(self.surf, color, points)

    def get_saved_status(self) -> str:
        if shared.file_name is None:
            return ""

        if shared.saved:
            return ""

        return "*"

    def get_file_name(self) -> str | None:
        if shared.file_name is None:
            return

        return self.get_saved_status() + Path(shared.file_name).name

    def add_loc(self, n_chars: int, out_str: str):
        loc_str = f"{shared.cursor_pos.x + 1},{shared.cursor_pos.y + 1}"
        out_str += " " * (n_chars - len(out_str) - len(loc_str) - 1)
        out_str += loc_str

        return out_str

    def add_interpreter_info(self, n_chars: int, out_str: str) -> str:
        info_str = f" {VENV_STR}{VERSION_STR}"
        # out_str += " " * (n_chars - len(out_str) - len(info_str) - 1)
        self.render_polygon(
            out_str, len(info_str), color=self.color.lerp(shared.theme["dark-fg"], 0.4)
        )
        out_str += info_str

        return out_str

    def add_file_name(self, out_str: str) -> str:
        file_name = self.get_file_name()
        if file_name is None:
            return out_str

        out_str += " "
        file_name = f" {file_name} "
        self.render_polygon(
            out_str,
            len(file_name),
            color=self.color.lerp(shared.theme["dark-fg"], 0.2),
        )
        out_str += f"{file_name}"

        return out_str

    def action_queue_to_str(self) -> str:
        return shared.action_str

    def add_action_queue(self, n_chars: int, out_str: str) -> str:
        action_str = self.action_queue_to_str()
        out_str += " " * (n_chars - len(out_str) - len(action_str) - 1)
        out_str += action_str

        return out_str

    def gen_surf(self):
        # out_str = self.status_str.format(
        #     saved=self.get_saved_status(),
        #     file_name=self.get_file_name(),
        #     mode=shared.mode.name,
        #     loc=f"{shared.cursor_pos.x}, {shared.cursor_pos.y}",
        # )
        self.surf = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT))
        self.color = pygame.Color(shared.theme["light-bg"])
        self.surf.fill(self.color)

        n_chars = int(shared.srect.width / shared.FONT_WIDTH)
        out_str = f"--{shared.mode.name}--"
        out_str = self.add_file_name(out_str)
        # out_str = self.add_loc(n_chars, out_str)

        if shared.file_name is not None and shared.file_name.endswith(".py"):
            out_str = self.add_interpreter_info(n_chars, out_str)
        out_str = self.add_action_queue(n_chars, out_str)
        render_at(
            self.surf,
            shared.FONT.render(out_str, True, shared.theme["default-fg"]),
            "midleft",
            (5, 0),
        )

    def on_cmd(self) -> None:
        if not shared.typing_cmd:
            return

        self.command_bar.update()

    def update(self):
        if shared.typing_cmd or (
            shared.mode == FileState.NORMAL
            and shared.action_queue
            and shared.action_queue[-1].endswith(":")
        ):
            shared.typing_cmd = True
            shared.action_queue.clear()
        else:
            self.command_bar.text = ""

        self.on_cmd()

    def draw(self):
        self.gen_surf()

        if shared.typing_cmd and not shared.selecting_file:
            self.command_bar.draw()

            size = (
                self.surf.get_width(),
                self.command_bar.surf.get_height() + self.surf.get_height(),
            )
            temp = pygame.Surface(size, pygame.SRCALPHA)

            render_at(temp, self.command_bar.surf, "topleft")
            render_at(temp, self.surf, "bottomleft")

            self.surf = temp
