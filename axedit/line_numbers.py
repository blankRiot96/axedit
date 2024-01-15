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
            text = shared.FONT.render(str(i + 1), True, "white")
            text.set_alpha(150)
            if i == shared.cursor_pos.y:
                text.set_alpha(255)
            self.surf.blit(text, (shared.FONT_WIDTH, i * shared.FONT_HEIGHT))
