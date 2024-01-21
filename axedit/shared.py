import inspect
import typing as t
from pathlib import Path

import pygame

from axedit.state_enums import FileState

pygame.font.init()

# Constants
font_size: int = 24
APP_NAME = "axe"
FONT_PATH = Path(
    Path(__file__).parent / "assets/fonts/IntoneMonoNerdFontMono-Regular.ttf"
)
FONT = pygame.font.Font(FONT_PATH, font_size)
FONT_WIDTH = FONT.render("w", True, "white").get_width()
FONT_HEIGHT = FONT.get_height()
AXE_FOLDER_PATH = Path(inspect.getfile(inspect.currentframe())).parent
ASSETS_FOLDER = AXE_FOLDER_PATH / "assets"


# Shared Variables
class Pos:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class CharList(list):
    def _on_char_change(self):
        global chars_changed
        chars_changed = True

        if (
            self
            and isinstance(self[0], str)
            and ("".join(self).startswith("import") or "".join(self).startswith("from"))
        ):
            global import_line_changed
            import_line_changed = True

    def append(self, item):
        super().append(item)
        self._on_char_change()

    def extend(self, iterable):
        super().extend(iterable)
        self._on_char_change()

    def insert(self, index, item):
        super().insert(index, item)
        self._on_char_change()

    def remove(self, item):
        super().remove(item)
        self._on_char_change()

    def pop(self, index=-1):
        popped_item = super().pop(index)
        self._on_char_change()
        return popped_item

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._on_char_change()

    def __delitem__(self, index):
        super().__delitem__(index)
        self._on_char_change()


chars: CharList[list[str]] = CharList([CharList([])])
cursor_pos: Pos = Pos(0, 0)
screen: pygame.Surface
srect: pygame.Rect
events: list[pygame.event.Event]
mouse_pos: pygame.Vector2
keys: list[bool]
dt: float
cursor: object
mode: FileState = FileState.NORMAL
file_name: str | None = None
registered_number: int = 1
autocompleting = False
text_writing = False
naming_file: bool
chars_changed: bool
saved: bool
frame_cache: dict[t.Callable, t.Any]
import_line_changed: bool
