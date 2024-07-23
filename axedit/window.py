import typing as t

import pygame

from axedit.internals import Internals
from axedit.state_manager import StateManager


class Window:
    """Manages Axedit's window"""

    def __init__(self) -> None:
        self._internals = Internals()
        self._win_init()
        self.state_manager = StateManager(self._internals)

    def _win_init(self):
        self._screen = pygame.display.set_mode(
            self._internals.window_rect.size, pygame.RESIZABLE, vsync=1
        )

    def _update(self):
        self._internals.queue_input()
        self.state_manager.update()

    def _draw(self):
        self._screen.fill("black")
        self.state_manager.draw()
        pygame.display.flip()

    def run(self) -> t.NoReturn:
        """Runs the window"""
        while True:
            self._update()
            self._draw()
