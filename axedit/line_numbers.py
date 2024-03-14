import pygame
from axedit.logs import logger


from axedit import shared


class LineNumbers:
    def __init__(self) -> None:
        self.gen_blank()

    def gen_blank(self) -> None:
        self.surf = pygame.Surface(
            (
                shared.FONT_WIDTH * shared.line_number_digits,
                len(shared.chars) * shared.FONT_HEIGHT,
            ),
            pygame.SRCALPHA,
        )

    def update(self):
        end_of_page_lno = int(shared.srect.height / (shared.FONT_HEIGHT * 2))
        max_line_digits = len(f"{shared.cursor_pos.y + 1 + end_of_page_lno:.0f}")
        shared.line_number_digits = max_line_digits + 4

        # logger.debug(
        #     f"{end_of_page_lno=}, {max_line_digits=}, {shared.line_number_digits=}"
        # )

    def draw(self):
        self.gen_blank()
        for i in range(len(shared.chars)):
            alpha = 150
            num = abs(shared.cursor_pos.y - i)
            if i == shared.cursor_pos.y:
                alpha = 255
                num = i + 1
                num = " " + str(num)

            text = shared.FONT.render(str(num), True, shared.theme["default-fg"])
            text.set_alpha(alpha)

            self.surf.blit(text, (shared.FONT_WIDTH, i * shared.FONT_HEIGHT))
