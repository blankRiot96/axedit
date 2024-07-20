import typing as t

import pygame

from axedit.internals import Internals


class Window:
    """Manages Axedit's window"""

    def __init__(self) -> None:
        self._win_init()
        self._internals = Internals()

    def _win_init(self):
        self._screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE, vsync=1)

    def _update(self):
        self._internals.queue_input()

    def _draw(self):
        self._screen.fill("black")
        pygame.display.flip()

    def run(self) -> t.NoReturn:
        """Runs the window"""
        while True:
            self._update()
            self._draw()
