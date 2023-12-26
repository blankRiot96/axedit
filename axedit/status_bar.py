import pygame

from axedit import shared
from axedit.utils import render_at


class StatusBar:
    """
    file_name -> None
    loc -> shared.cursor_pos
    mode -> shared.mode
    """

    def __init__(self) -> None:
        self.status_str = "FILE: {file_name} | MODE: {mode} | LOC: {loc}"
        self.gen_surf()

    def gen_surf(self):
        out_str = self.status_str.format(
            file_name=shared.file_name,
            mode=shared.mode.name,
            loc=f"{shared.cursor_pos.x}, {shared.cursor_pos.y}",
        )
        self.surf = pygame.Surface(
            (shared.srect.width, shared.FONT_HEIGHT + shared.FONT_WIDTH)
        )
        self.surf.fill((48, 25, 52))
        render_at(
            self.surf, shared.FONT.render(out_str, True, "white"), "midleft", (5, 0)
        )

    def update(self):
        ...

    def draw(self):
        self.gen_surf()
