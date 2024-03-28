from __future__ import annotations

import inspect
import typing as t
from pathlib import Path

import pygame
import tomlkit

from axedit.state_enums import FileState

if t.TYPE_CHECKING:
    from axedit.autocompletions import AutoCompletions
    from axedit.classes import CharList, Pos
    from axedit.cursor import Cursor
    from axedit.linter import Linter

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
mouse_press: tuple[int, ...]
keys: list[bool]
kp: list[bool]
kr: list[bool]
dt: float

# Objects
chars: CharList[CharList[str]]
cursor_pos: Pos
cursor: Cursor
visual_mode_axis: Pos
autocompletion: AutoCompletions
linter: Linter

# Config
mode: FileState = FileState.NORMAL
file_name: str | None = None
theme: dict
config: tomlkit.TOMLDocument

# Registers
frame_cache: dict[t.Callable, t.Any]
registered_number: int = 1
action_queue: list[str]
action_str: str
scroll: pygame.Vector2
line_number_digits: int = 6

# Flags
autocompleting = False
text_writing = False
theme_changed = False
running = True
handling_scroll_bar = False
naming_file: bool
chars_changed: bool
saved: bool
import_line_changed: bool
actions_modified: bool
typing_cmd: bool
