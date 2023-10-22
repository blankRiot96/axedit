from functools import partial

import pygame

from src import shared
from src.state_enums import EditorState
from src.utils import AcceleratedKeyPress, Time


class Cursor:
    KEYS = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
    }

    def __init__(self) -> None:
        self.gen_image()
        self.pos = pygame.Vector2()
        self.alpha = 255
        self.blink_speed = 350
        self.direction = -1
        self.accels = [
            AcceleratedKeyPress(key, partial(self.handle_input, key))
            for key in self.KEYS
        ]
        self.move_timer = Time(0.5)

    def gen_image(self):
        self.image = pygame.Surface((shared.FONT_WIDTH, shared.FONT_HEIGHT))
        self.image.fill("white")

    def move(self):
        self.pos.x = shared.cursor_pos.x * shared.FONT_WIDTH
        self.pos.y = shared.cursor_pos.y * shared.FONT_HEIGHT

    def blink(self):
        delta_alpha = self.blink_speed * shared.dt
        delta_alpha *= self.direction

        self.alpha += delta_alpha

        if self.alpha < 0 or self.alpha > 255:
            self.direction *= -1

        self.image.set_alpha(self.alpha)

    def handle_arrows(self, key: int):
        move = Cursor.KEYS.get(key)
        if move is None:
            return

        if shared.cursor_pos.x + move[0] >= 0:
            shared.cursor_pos.x += move[0]

        if shared.cursor_pos.y + move[1] >= 0:
            shared.cursor_pos.y += move[1]

        if len(shared.chars) - 1 < shared.cursor_pos.y:
            shared.chars.insert(shared.cursor_pos.y, [])
        if (line_len := len(shared.chars[shared.cursor_pos.y])) < shared.cursor_pos.x:
            diff = shared.cursor_pos.x - line_len
            shared.chars[shared.cursor_pos.y].extend([" "] * diff)

    def handle_normals(self):
        ...

    def handle_input(self, key):
        self.handle_arrows(key)

    def update_accels(self):
        for accel in self.accels:
            accel.update(shared.events, shared.keys)

    def update(self):
        self.move()
        self.blink()
        self.update_accels()

    def draw(self, editor_surf: pygame.Surface):
        editor_surf.blit(self.image, self.pos)
