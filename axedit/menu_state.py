import typing as t

import pygame

from axedit import shared
from axedit.cmd_bar import CommandBar
from axedit.file_selector import FileSelector
from axedit.funcs import get_icon
from axedit.logs import logger
from axedit.state_enums import State
from axedit.utils import render_at

Command: t.TypeAlias = list[str, str]
MenuLines: t.TypeAlias = list[Command]


class MenuTexter:
    """Basically renders the menu help text in a cute manner"""

    def __init__(self, lines: MenuLines) -> None:
        self.lines = lines.copy()
        if isinstance(shared.config["font"]["path"], str):
            self.font = pygame.Font(shared.FONT_PATH, 22)
        elif shared.config["font"]["family"]:
            self.font = pygame.sysfont.SysFont(shared.config["font"]["family"], 22)
        self.font_width, self.font_height = self.font.render(
            " ", True, "white"
        ).get_size()
        self.gen_surf()

    def gen_surf(self) -> None:
        """Generates the image"""

        size_big = len("".join(self.lines[0]))
        for item in self.lines:
            temp_big = len("".join(item))
            if temp_big > size_big:
                size_big = temp_big

        surf_width = size_big * self.font_width * 2
        surf_height = self.font_height * len(self.lines)
        self.surf = pygame.Surface(
            (surf_width + self.font_width, surf_height), pygame.SRCALPHA
        )

        desc_surf = self.render_description()
        self.surf.blit(desc_surf, (0, 0))
        self.surf.blit(
            self.render_commands(), (desc_surf.get_width() + self.font_width * 3, 0)
        )

        self.surf = self.surf.subsurface(self.surf.get_bounding_rect()).copy()

    def render_description(self) -> pygame.Surface:
        width = len(max(self.lines, key=lambda line: len(line[0]))[0])
        text = "".join(line[0].rjust(width) + "\n" for line in self.lines)

        return self.font.render(text, True, shared.theme["default-fg"])

    def render_commands(self) -> pygame.Surface:
        command_width = (
            len(max(self.lines, key=lambda line: len(line[1]))[1]) * self.font_width
        ) * 2
        command_height = self.surf.get_height()

        command_surf = pygame.Surface((command_width, command_height), pygame.SRCALPHA)

        for row, line in enumerate(self.lines):
            cmd = line[1]
            cmd = cmd.split()
            acc_x = 0
            for word in cmd:
                flagged = False
                if word.startswith("`"):
                    word = word[1:-1]
                    flagged = True
                word = f" {word} "

                rect = pygame.Rect(
                    acc_x,
                    row * self.font_height,
                    len(word) * self.font_width,
                    self.font_height,
                )

                if flagged:
                    pygame.draw.rect(command_surf, (30, 30, 30), rect, border_radius=3)

                command_surf.blit(
                    self.font.render(word, True, shared.theme["default-fg"]), rect
                )
                acc_x += rect.width

        return command_surf

    def update(self): ...


class MenuState:
    LINES = [
        ["Command Bar", "`:`"],
        ["Fullscreen", "`F11`"],
        ["New File", "`Ctrl` + `N`"],
        ["Open File", "`Ctrl` + `P`"],
    ]

    def __init__(self) -> None:
        self.next_state = None
        shared.typing_cmd = False
        self.gen_logo()

        self.command_bar = CommandBar()
        self.texter = MenuTexter(MenuState.LINES)
        self.file_selector: None | FileSelector = None

    def gen_logo(self):
        self.logo: pygame.Surface = get_icon(shared.theme["select-bg"])
        self.logo = self.logo.subsurface(self.logo.get_bounding_rect()).copy()
        self.logo = pygame.transform.smoothscale_by(self.logo, 0.75)

    def on_ctrl_p(self):
        if not shared.keys[pygame.K_p]:
            return

        shared.selecting_file = True

    def on_ctrl_n(self):
        if not shared.keys[pygame.K_n]:
            return
        self.next_state = State.EDITOR

    def on_ctrl_t(self): ...

    def update(self):
        if shared.selecting_file and self.file_selector is None:
            self.file_selector = FileSelector()
        if not shared.selecting_file and self.file_selector is not None:
            self.file_selector = None

        for event in shared.events:
            if event.type == pygame.TEXTINPUT and event.text == ":":
                shared.typing_cmd = True

        self.texter.update()
        if not shared.selecting_file:
            self.command_bar.update()
            self.next_state = self.command_bar.next_state

        if shared.keys[pygame.K_LCTRL] or shared.keys[pygame.K_RCTRL]:
            self.on_ctrl_p()
            self.on_ctrl_n()
            self.on_ctrl_t()

        if shared.theme_changed:
            self.gen_logo()

        if self.file_selector is not None:
            self.file_selector.update()
            self.next_state = self.file_selector.next_state

    def draw(self):
        if not shared.selecting_file:
            self.command_bar.draw()
        dist_between_em = 70
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
        if shared.typing_cmd:
            render_at(shared.screen, self.command_bar.surf, "bottomright")

        if self.file_selector is not None:
            self.file_selector.draw()
