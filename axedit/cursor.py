from functools import partial

import pygame

from axedit import shared
from axedit.state_enums import FileState
from axedit.utils import AcceleratedKeyPress, Time


class Cursor:
    KEYS = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
    }
    NORMAL_KEYS = {
        pygame.K_j: (-1, 0),
        pygame.K_l: (1, 0),
        pygame.K_i: (0, -1),
        pygame.K_k: (0, 1),
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
        self.normal_accels = [
            AcceleratedKeyPress(key, partial(self.handle_input, key))
            for key in self.NORMAL_KEYS
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

    def handle_cursor_delta(self, move: tuple):
        if shared.cursor_pos.x + move[0] >= 0:
            shared.cursor_pos.x += move[0]

        if shared.cursor_pos.y + move[1] >= 0:
            shared.cursor_pos.y += move[1]

        if move[0] < 0 and shared.cursor_pos.x == 0:
            shared.cursor_pos.y -= 1
            shared.cursor_pos.y = max(0, shared.cursor_pos.y)
            return

        if len(shared.chars) - 1 < shared.cursor_pos.y:
            shared.chars.insert(shared.cursor_pos.y, [])
        if (line_len := len(shared.chars[shared.cursor_pos.y])) < shared.cursor_pos.x:
            # diff = shared.cursor_pos.x - line_len
            # shared.chars[shared.cursor_pos.y].extend([" "] * diff)

            if move[1] == 0:
                shared.cursor_pos.y += 1

            shared.cursor_pos.x = line_len - 1

            shared.cursor_pos.x = max(0, shared.cursor_pos.x)

    def handle_arrows(self, key: int):
        move = Cursor.KEYS.get(key)
        if move is None:
            return

        self.handle_cursor_delta(move)

    def purifier(self, line):
        # out = ""
        # for char in line:
        #     if not char.isalnum():
        #         char = " "
        #     out += char
        # out = out.strip()
        # return out
        return line.strip()

    def get_cursor_shift(self, remaining_line: list):
        cursor_shift = 0
        remaining_line = "".join(remaining_line)
        purified = self.purifier(remaining_line)
        for char in purified:
            if char in (" ", ".", ":"):
                break

            cursor_shift += 1

        cursor_shift += len(remaining_line) - len(purified)
        print(cursor_shift)
        return cursor_shift

    def handle_normals(self, key: int):
        move = Cursor.NORMAL_KEYS.get(key)
        if move is None:
            return

        if shared.keys[pygame.K_LSHIFT]:
            line = shared.chars[shared.cursor_pos.y]
            if move[0] > 0:
                remaining = line[shared.cursor_pos.x :]
            else:
                remaining = line[: shared.cursor_pos.x]
            cursor_shift = self.get_cursor_shift(remaining)
            move = (move[0] * cursor_shift, move[1])

        self.handle_cursor_delta(move)

    def handle_input(self, key):
        self.handle_arrows(key)

        if shared.mode == FileState.NORMAL:
            for _ in range(shared.registered_number):
                self.handle_normals(key)

    def update_accels(self):
        if shared.autocompleting:
            return
        for accel in self.accels:
            accel.update(shared.events, shared.keys)

        if shared.mode != FileState.NORMAL:
            return

        for accel in self.normal_accels:
            accel.update(shared.events, shared.keys)

    def update(self):
        self.move()
        self.blink()
        self.update_accels()

    def draw(self, editor_surf: pygame.Surface):
        editor_surf.blit(self.image, self.pos)
