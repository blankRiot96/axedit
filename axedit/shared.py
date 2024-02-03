from __future__ import annotations

import inspect
import typing as t
from pathlib import Path

import pygame

from axedit.state_enums import FileState

if t.TYPE_CHECKING:
    from axedit.classes import CharList, Pos
    from axedit.cursor import Cursor

pygame.font.init()

# Constants
FONT_SIZE: int = 24
APP_NAME = "axe"
AXE_FOLDER_PATH = Path(inspect.getfile(inspect.currentframe())).parent
ASSETS_FOLDER = AXE_FOLDER_PATH / "assets"
FONT_PATH = ASSETS_FOLDER / "fonts/IntoneMonoNerdFontMono-Regular.ttf"
FONT = pygame.font.Font(FONT_PATH, FONT_SIZE)
FONT_WIDTH = FONT.render("w", True, "white").get_width()
FONT_HEIGHT = FONT.get_height()
THEMES_PATH = ASSETS_FOLDER / "data/themes"

# Core
screen: pygame.Surface
srect: pygame.Rect

# Events
events: list[pygame.event.Event]
mouse_pos: pygame.Vector2
keys: list[bool]
kp: list[bool]
kr: list[bool]
dt: float

# Objects
chars: CharList[CharList[str]]
cursor_pos: Pos
cursor: Cursor

# Config
mode: FileState = FileState.NORMAL
file_name: str | None = None
# Default is catppuccin-mocha
theme: dict = {
    "default-bg": "#1e1e2e",
    "light-bg": "#b4befe",
    "select-bg": "#313244",
    "comment": "#45475a",
    "dark-fg": "#585b70",
    "default-fg": "#cdd6f4",
    "light-fg": "#f5e0dc",
    "var": "#f38ba8",
    "const": "#fab387",
    "class": "#f9e2af",
    "string": "#a6e3a1",
    "match": "#94e2d5",
    "func": "#89b4fa",
    "keyword": "#cba6f7",
    "dep": "#f2cdcd",
}

# Registers
frame_cache: dict[t.Callable, t.Any]
registered_number: int = 1
action_queue: list[str]
scroll: pygame.Vector2

# Flags
autocompleting = False
text_writing = False
theme_changed = False
naming_file: bool
chars_changed: bool
saved: bool
import_line_changed: bool
actions_modified: bool
typing_cmd: bool
