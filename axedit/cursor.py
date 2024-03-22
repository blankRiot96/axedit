from functools import partial

import clipboard
import pygame

from axedit import shared
from axedit.classes import CharList
from axedit.funcs import center_cursor
from axedit.input_queue import AcceleratedKeyPress, RegexManager
from axedit.logs import logger
from axedit.modal import *
from axedit.state_enums import FileState
from axedit.utils import Time


class Cursor:
    KEYS = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
    }
    NORMAL_KEYS = {
        pygame.K_h: (-1, 0),
        pygame.K_l: (1, 0),
        pygame.K_k: (0, -1),
        pygame.K_j: (0, 1),
    }

    def __init__(self) -> None:
        self.gen_image()
        self.pos = pygame.Vector2()
        self.rect = self.image.get_rect(topleft=self.pos)
        self.blink_timer = Time(0.5)
        self.cursor_visible = True
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
        self.regex_manager = RegexManager(
            {
                r"^(\d+)?(dd|d\d+d)$": on_dd,
                "zz": on_zz,
                "gg": on_gg,
                "G": on_G,
                r"p": on_p,
                r"\$": on_dollar_sign,
                "0": on_zero,
                r"\}": on_right_brace,
                r"\{": on_left_brace,
            }
        )

    def gen_image(self):
        self.image = pygame.Surface((shared.FONT_WIDTH, shared.FONT_HEIGHT))
        self.image.fill(shared.theme["default-fg"])

    def move(self):
        self.pos.x = (shared.cursor_pos.x * shared.FONT_WIDTH) - shared.scroll.x
        self.pos.y = (shared.cursor_pos.y * shared.FONT_HEIGHT) + shared.scroll.y

    def blink(self):
        if self.blink_timer.tick():
            self.cursor_visible = not self.cursor_visible

    def handle_cursor_delta(self, move: tuple):
        self.cursor_visible = True
        self.blink_timer.reset()

        line_len = len(shared.chars[shared.cursor_pos.y])
        limit = 0 if shared.mode == FileState.INSERT else -1

        # Make sure that the cursor cant be moved into unknown regions
        if shared.cursor_pos.x + move[0] >= 0:
            if shared.cursor_pos.x == line_len + limit and move[0] > 0:
                # shared.cursor_pos.x += move[0]
                ...
            else:
                shared.cursor_pos.x += move[0]

        if shared.cursor_pos.y + move[1] >= 0:
            shared.cursor_pos.y += move[1]

        if len(shared.chars) - 1 < shared.cursor_pos.y:
            shared.cursor_pos.y -= 1
        if line_len < shared.cursor_pos.x:
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
        return cursor_shift

    def handle_normals(self, key: int):
        move = Cursor.NORMAL_KEYS.get(key)
        if move is None:
            return

        # if shared.keys[pygame.K_LSHIFT]:
        #     line = shared.chars[shared.cursor_pos.y]
        #     if move[0] > 0:
        #         remaining = line[shared.cursor_pos.x :]
        #     else:
        #         remaining = line[: shared.cursor_pos.x]
        #     cursor_shift = self.get_cursor_shift(remaining)
        #     move = (move[0] * cursor_shift, move[1])

        self.handle_cursor_delta(move)

    def register_adjust(self):
        if not shared.action_queue:
            return
        if shared.action_queue[-1] in "jk":
            shared.registered_number = min(shared.registered_number, len(shared.chars))
        elif shared.action_queue[-1] in "hl":
            shared.registered_number = min(
                shared.registered_number, len(shared.chars[shared.cursor_pos.y])
            )

    def handle_input(self, key):
        self.handle_arrows(key)

        if shared.mode in (FileState.NORMAL, FileState.VISUAL):
            self.register_adjust()
            for _ in range(shared.registered_number):
                self.handle_normals(key)

            visible_region = pygame.Rect(0, shared.scroll.y, *shared.srect.size)
            # if ((shared.cursor_pos.y - 1) * shared.FONT_HEIGHT) > shared.scroll.y:
            if not self.rect.colliderect(visible_region):
                center_cursor()
            shared.action_queue.clear()
            shared.registered_number = 1

    def update_accels(self):
        if shared.autocompleting:
            return
        for accel in self.accels:
            accel.update()

        if shared.mode not in (FileState.NORMAL, FileState.VISUAL):
            return

        for accel in self.normal_accels:
            accel.update()

    def bound_cursor(self):
        if shared.cursor_pos.y >= len(shared.chars):
            shared.cursor_pos.y = len(shared.chars) - 1

        row_len = len(shared.chars[shared.cursor_pos.y])
        if shared.cursor_pos.x > row_len - 1:
            shared.cursor_pos.x = row_len

    def highlight_selected_text(self, editor_surf: pygame.Surface):
        options_x = (shared.cursor_pos.x, shared.visual_mode_axis.x)
        options_y = (shared.cursor_pos.y, shared.visual_mode_axis.y)

        lower_meniscus_x = min(options_x)
        upper_meniscus_x = max(options_x)

        lower_meniscus_y = min(options_y)
        upper_meniscus_y = max(options_y)

        final_surf = pygame.Surface(
            (
                shared.srect.width,
                (upper_meniscus_y - lower_meniscus_y + 1) * shared.FONT_HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        if shared.action_str == "d":
            lower_line = shared.chars[lower_meniscus_y]
            upper_line = shared.chars[upper_meniscus_y]

        lines_to_delete = []
        copy_output = ""
        for i, row in enumerate(range(lower_meniscus_y, upper_meniscus_y + 1)):
            size = 0
            offset = 0

            if lower_meniscus_y == upper_meniscus_y:
                size = upper_meniscus_x - lower_meniscus_x + 1
                offset = lower_meniscus_x
            elif row == shared.visual_mode_axis.y:
                if row == lower_meniscus_y:
                    size = len(shared.chars[row]) - shared.visual_mode_axis.x
                    offset = shared.visual_mode_axis.x
                else:
                    size = shared.visual_mode_axis.x + 1
                    offset = 0
            elif row == shared.cursor_pos.y:
                if row == lower_meniscus_y:
                    size = len(shared.chars[row]) - shared.cursor_pos.x
                    offset = shared.cursor_pos.x
                else:
                    size = shared.cursor_pos.x
            else:
                size = len(shared.chars[row])
                if size == 0:
                    size = 1

            if shared.action_str == "d":
                copy_output += "".join(shared.chars[row][offset : size + offset]) + "\n"
                del shared.chars[row][offset : size + offset]
                if not shared.chars[row]:
                    lines_to_delete.append(row)
                continue
            row_size = size * shared.FONT_WIDTH
            row_image = pygame.Surface((row_size, shared.FONT_HEIGHT), pygame.SRCALPHA)
            row_image.fill(shared.theme["default-fg"])
            row_image.set_alpha(50)

            final_surf.blit(
                row_image, (offset * shared.FONT_WIDTH, i * shared.FONT_HEIGHT)
            )

        for line in lines_to_delete[::-1]:
            shared.chars.pop(line)
            # shared.cursor_pos.y = line
            if not shared.chars:
                shared.chars.append(CharList([]))

        if shared.action_str == "d":
            # Join the two half eaten lines
            shared.chars[lower_meniscus_y] = lower_line + upper_line
            try:
                shared.chars.pop(lower_meniscus_y + 1)
            except IndexError:
                pass
            # shared.cursor_pos = Pos(
            #     shared.visual_mode_axis.x, shared.visual_mode_axis.y
            # )

            # Copy the deleted content to the clipboard
            clipboard.copy(copy_output)

        if shared.cursor_pos.y < shared.visual_mode_axis.y:
            offset = 0
        else:
            offset = -final_surf.get_height() + shared.FONT_HEIGHT

        editor_surf.blit(final_surf, (-shared.scroll.x, offset + self.pos.y))
        on_d()

    def update(self):
        if shared.typing_cmd:
            return
        self.blink()
        self.update_accels()
        self.regex_manager.update()
        self.bound_cursor()
        self.move()
        self.rect.topleft = self.pos

    def draw(self, editor_surf: pygame.Surface):
        if shared.mode == FileState.INSERT and not self.cursor_visible:
            return

        if shared.mode == FileState.VISUAL:
            self.highlight_selected_text(editor_surf)
        editor_surf.blit(self.image, self.pos)

        try:
            char = shared.chars[shared.cursor_pos.y][shared.cursor_pos.x]
        except IndexError:
            return
        char_surf = shared.FONT.render(char, True, shared.theme["default-bg"])
        editor_surf.blit(char_surf, self.pos)
