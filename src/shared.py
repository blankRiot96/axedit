from pathlib import Path

import pygame

pygame.font.init()

# Constants
font_size: int = 24
FONT_PATH = Path("assets/fonts/IntoneMonoNerdFontMono-Regular.ttf")
FONT = pygame.font.Font(FONT_PATH, font_size)


# Shared Variables
cursor_pos: pygame.Vector2 = pygame.Vector2()
screen: pygame.Surface
events: list[pygame.event.Event]
keys: list[bool]
dt: float
cursor: object
