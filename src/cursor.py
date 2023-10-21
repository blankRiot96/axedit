import pygame

from src import shared
from src.utils import EventManager, Time


class Cursor:
    KEYS = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
    }

    def __init__(self) -> None:
        self.width = shared.FONT.render("w", True, "white").get_width()
        self.height = shared.FONT.get_height()
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill("white")
        self.pos = pygame.Vector2()
        self.alpha = 255
        self.blink_speed = 350
        self.direction = -1
        self.event_manager = EventManager({pygame.KEYDOWN: self.handle_input})
        self.move_timer = Time(0.5)

    def move(self):
        self.pos.x = shared.cursor_pos.x * self.width
        self.pos.y = shared.cursor_pos.y * self.height

    def blink(self):
        delta_alpha = self.blink_speed * shared.dt
        delta_alpha *= self.direction

        self.alpha += delta_alpha

        if self.alpha < 0 or self.alpha > 255:
            self.direction *= -1

        self.image.set_alpha(self.alpha)

    def handle_input(self, event: pygame.Event):
        move = Cursor.KEYS.get(event.key)
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

    def update(self):
        self.move()
        self.blink()
        self.event_manager.update(shared.events)

    def draw(self):
        shared.screen.blit(self.image, self.pos)
