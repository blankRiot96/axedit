from pathlib import Path

import pygame

pygame.font.init()

# Constants
font_size: int = 24
FONT_PATH = Path("assets/fonts/IntoneMonoNerdFontMono-Regular.ttf")
FONT = pygame.font.Font(FONT_PATH, font_size)


# Shared Variables
class Pos:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


chars: list[list[str]] = [[]]
cursor_pos: Pos = Pos(0, 0)
screen: pygame.Surface
events: list[pygame.event.Event]
keys: list[bool]
dt: float
cursor: object
