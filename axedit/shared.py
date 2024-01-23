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
FONT_PATH = Path(
    Path(__file__).parent / "assets/fonts/IntoneMonoNerdFontMono-Regular.ttf"
)
FONT = pygame.font.Font(FONT_PATH, FONT_SIZE)
FONT_WIDTH = FONT.render("w", True, "white").get_width()
FONT_HEIGHT = FONT.get_height()
AXE_FOLDER_PATH = Path(inspect.getfile(inspect.currentframe())).parent
ASSETS_FOLDER = AXE_FOLDER_PATH / "assets"

# Core
screen: pygame.Surface
srect: pygame.Rect

# Events
events: list[pygame.event.Event]
mouse_pos: pygame.Vector2
keys: list[bool]
kp: list[bool]
dt: float

# Objects
chars: CharList[CharList[str]]
cursor_pos: Pos
cursor: Cursor

# Config
mode: FileState = FileState.NORMAL
file_name: str | None = None
frame_cache: dict[t.Callable, t.Any]

# Flags
registered_number: int = 1
autocompleting = False
text_writing = False
naming_file: bool
chars_changed: bool
saved: bool
import_line_changed: bool
