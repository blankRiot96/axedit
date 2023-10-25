from pathlib import Path

import pygame

from src.state_enums import FileState

pygame.font.init()

# Constants
font_size: int = 24
FONT_PATH = Path("assets/fonts/IntoneMonoNerdFontMono-Regular.ttf")
FONT = pygame.font.Font(FONT_PATH, font_size)
FONT_WIDTH = FONT.render("w", True, "white").get_width()
FONT_HEIGHT = FONT.get_height()


# Shared Variables
class Pos:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


chars: list[list[str]] = [[]]
cursor_pos: Pos = Pos(0, 0)
screen: pygame.Surface
srect: pygame.Rect
events: list[pygame.event.Event]
keys: list[bool]
dt: float
cursor: object
mode: FileState = FileState.NORMAL
file_name: str | None = None
registered_number: int = 1
autocompleting = False
text_writing = False
