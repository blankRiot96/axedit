import pygame

from axedit import shared


class LineNumbers:
    def __init__(self) -> None:
        self.surf = pygame.Surface(
            (shared.FONT_WIDTH * 5, len(shared.chars) * shared.FONT_HEIGHT),
            pygame.SRCALPHA,
        )

    def update(self):
        ...

    def draw(self):
        self.surf = pygame.Surface(
            (shared.FONT_WIDTH * 5, len(shared.chars) * shared.FONT_HEIGHT),
            pygame.SRCALPHA,
        )
        for i in range(len(shared.chars)):
            alpha = 150
            num = abs(shared.cursor_pos.y - i)
            if i == shared.cursor_pos.y:
                alpha = 255
                num = i + 1
                num = " " + str(num)

            text = shared.FONT.render(str(num), True, "white")
            text.set_alpha(alpha)

            self.surf.blit(text, (shared.FONT_WIDTH, i * shared.FONT_HEIGHT))
