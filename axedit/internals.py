import typing as t
from pathlib import Path

import pygame

from axedit.enums import AppState


class Internals:
    """Provides internals information via a strict API"""

    _REGISTERED_INFO = {}

    def __init__(self) -> None:
        self._clock = pygame.Clock()
        self.dt = 0.0
        self.events: list[pygame.Event] = []
        self.next_app_state: AppState | None = None
        self.window_rect = pygame.Rect(0, 0, 1100, 650)

    @classmethod
    def register_path_selection(cls, path: Path) -> None:
        """Registers the selected file/fodler to open"""

        if path.is_dir():
            cls._REGISTERED_INFO["path_type"] = "dir"
        else:
            cls._REGISTERED_INFO["path_type"] = "file"
        cls._REGISTERED_INFO["path"] = path

    def queue_input(self):
        """Queue the input received by the window"""

        self.dt = self._clock.tick()
        self.events = pygame.event.get()

        for event in self.events:
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.VIDEORESIZE:
                self.window_rect.size = event.size