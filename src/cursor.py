import pygame

from src import shared
from src.utils import render_at


class Cursor:
    def __init__(self) -> None:
        self.width = shared.FONT.render("w", True, "white").get_width()
        self.height = shared.FONT.get_height()
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill("white")
        self.pos = pygame.Vector2()
        self.alpha = 255
        self.blink_speed = 350
        self.direction = -1

    def move(self):
        self.pos.x = shared.cursor_pos.x * self.width
        self.pos.y = shared.cursor_pos.y * self.height

    def update(self):
        self.move()
        self.blink()

    def blink(self):
        delta_alpha = self.blink_speed * shared.dt
        delta_alpha *= self.direction

        self.alpha += delta_alpha

        if self.alpha < 0 or self.alpha > 255:
            self.direction *= -1

        self.image.set_alpha(self.alpha)

    def draw(self):
        shared.screen.blit(self.image, self.pos)
