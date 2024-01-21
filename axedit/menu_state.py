import typing as t

import pygame

from axedit import shared
from axedit.funcs import get_icon
from axedit.state_enums import State
from axedit.utils import render_at

Command: t.TypeAlias = list[str, str]
MenuLines: t.TypeAlias = list[Command]


class MenuTexter:
    """Basically renders the menu help text in a cute manner"""

    def __init__(self, lines: MenuLines) -> None:
        self.lines = lines.copy()
        self.gen_surf()

    def gen_surf(self) -> None:
        """Generates the image"""

        size_big = len("".join(self.lines[0]))
        for item in self.lines:
            temp_big = len("".join(item))
            if temp_big > size_big:
                size_big = temp_big

        surf_width = size_big * shared.FONT_WIDTH
        surf_height = shared.FONT_HEIGHT * len(self.lines)
        self.surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)

        self.surf.blit(self.render_description(), (0, 0))

    def render_description(self) -> pygame.Surface:
        text = "".join(line[0] + "\n" for line in self.lines)

        return shared.FONT.render(text, True, "white")

    def render_commands(self) -> pygame.Surface:
        command_width = len(max(self.lines, key=lambda line: len(line[1])))
        command_height = self.surf.get_height()

        command_surf = pygame.Surface((command_width, command_height), pygame.SRCALPHA)

        for line in self.lines:
            cmd = line[1]

    def update(self):
        ...


class MenuState:
    LINES = [
        ["Command Bar", "`:`"],
        ["Enter Editor", "`ESC`"],
        ["Toggle Fullscreen", "`F11`"],
        ["Open File", "`Ctrl` + `O`"],
        ["Start Tutorial", "`Ctrl` + `t`"],
    ]

    def __init__(self) -> None:
        self.next_state = None
        self.logo: pygame.Surface = get_icon()
        self.logo = self.logo.subsurface(self.logo.get_bounding_rect()).copy()
        self.logo = pygame.transform.smoothscale_by(self.logo, 0.75)

        self.texter = MenuTexter(MenuState.LINES)

    def update(self):
        self.texter.update()

    def draw(self):
        dist_between_em = 40
        render_at(
            shared.screen,
            self.logo,
            "center",
            (0, ((-self.texter.surf.get_height() - dist_between_em) / 2)),
        )
        render_at(
            shared.screen,
            self.texter.surf,
            "center",
            (0, (self.logo.get_height() + dist_between_em) / 2),
        )
