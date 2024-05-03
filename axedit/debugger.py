import pygame

from axedit import shared


class Debugger:
    """Displays some debug info"""

    def __init__(self) -> None:
        self.debug_info = ""

    def update(self):
        fps_string = f"{shared.clock.get_fps():.0f}"
        self.debug_info = fps_string

    def draw(self):
        debug_surf = shared.FONT.render(self.debug_info, True, "green")
        shared.screen.blit(debug_surf, (10, 10))
