import functools

import pygame

from axedit import shared
from axedit.funcs import is_event_frame
from axedit.logs import logger


@functools.lru_cache(maxsize=512)
def render_num(num: int, alpha: int, fg) -> pygame.Surface:
    text = shared.FONT.render(str(num), True, fg)
    text.set_alpha(alpha)
    return text


class LineNumbers:
    def __init__(self) -> None:
        self.gen_blank()
        self.last_scroll_offset = 0
        self.last_char_pos_y = 0
        self.to_render = True
        self.scroll_char_offset = 0
        self.once = True
        self.last_chars_length = len(shared.chars)

    def gen_blank(self) -> None:
        self.surf = pygame.Surface(
            (shared.FONT_WIDTH * shared.line_number_digits, shared.srect.height),
            pygame.SRCALPHA,
        )

    def update(self):
        end_of_page_lno = int(
            (shared.srect.height + shared.scroll.y) / shared.FONT_HEIGHT
        )
        max_line_digits = len(f"{shared.cursor_pos.y + end_of_page_lno:.0f}")
        shared.line_number_digits = max_line_digits + 4

        # logger.debug(
        #     f"{end_of_page_lno=}, {max_line_digits=}, {shared.line_number_digits=}"
        # )

    def is_to_be_rendered(self):
        if self.once:
            self.once = False
            return True

        self.scroll_char_offset = abs(int(shared.scroll.y / shared.FONT_HEIGHT))
        return (
            self.scroll_char_offset != self.last_scroll_offset
            or shared.cursor_pos.y != self.last_char_pos_y
            or len(shared.chars) != self.last_chars_length
            or is_event_frame(pygame.VIDEORESIZE)
        )

    def draw_lines(self):
        max_lines = int(shared.srect.height / shared.FONT_HEIGHT)
        for i in range(max_lines):
            alpha = 150

            lno = i + self.scroll_char_offset
            num = abs(shared.cursor_pos.y - lno)
            if lno == shared.cursor_pos.y:
                alpha = 255
                num = lno + 1
                num = " " + str(num)
            elif lno >= len(shared.chars):
                num = "~"

            text = render_num(num, alpha, shared.theme["default-fg"])

            # self.surf.blit(
            #     text,
            #     (shared.FONT_WIDTH, i * shared.FONT_HEIGHT),
            # )

            self.surf.fblits([(text, (shared.FONT_WIDTH, i * shared.FONT_HEIGHT))])

    def reset_modifiers(self):
        self.last_scroll_offset = self.scroll_char_offset
        self.last_char_pos_y = shared.cursor_pos.y
        self.last_chars_length = len(shared.chars)

    def draw(self):
        if not self.is_to_be_rendered():
            return

        self.gen_blank()
        self.draw_lines()
        self.reset_modifiers()
