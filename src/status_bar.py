import pygame

from src import shared


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
        self.surf = shared.FONT.render(out_str, True, "white")

    def update(self):
        ...

    def draw(self):
        self.gen_surf()
