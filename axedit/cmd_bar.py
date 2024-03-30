import abc
import itertools
import typing as t

import pygame

from axedit import shared
from axedit.funcs import reset_config, soft_save_file, write_config
from axedit.themes import apply_theme, get_available_theme_names
from axedit.utils import Time, render_at


def calculate_number_of_rows(
    cell_width, cell_height, total_cells, total_visible_width
) -> int:
    max_rows = 3
    total_width = cell_width * total_cells
    rows = 1 + (total_width // total_visible_width)

    return min(rows, max_rows)


class Command:
    def __init__(
        self,
        patterns: str | tuple[str],
        callback: t.Callable,
        subs: list[str] | None = None,
        subsidary_cmd: bool = False,
    ) -> None:
        self.patterns = patterns
        self.subs = [] if subs is None else subs
        self.callback = callback
        self.beauty_text = self.get_beauty_text()
        self.subsidary_cmd = subsidary_cmd

    def get_beauty_text(self) -> str:
        if isinstance(self.patterns, str):
            return self.patterns[1:]

        return max(self.patterns, key=len)[1:]

    def is_perfect_match(self, text: str) -> bool:
        if isinstance(self.patterns, str):
            return text == self.patterns
        else:
            return text in self.patterns

    def is_match(self, text: str) -> bool:
        pattern = self.get_beauty_text()
        search_text = text[1:]
        if not search_text:
            return self.subsidary_cmd

        text = itertools.cycle(search_text)
        current_search_char = next(text)
        passers = []
        for index, char in enumerate(pattern):
            if char == current_search_char:
                passers.append(index)
                if len(passers) == len(search_text):
                    break
                current_search_char = next(text)

        if len(passers) == len(search_text):
            return True

        return False

    def execute_cmd(self, text: str) -> None:
        if self.is_perfect_match(text):
            self.callback()

    def get_surf(self, selected: bool = False) -> pygame.Surface:
        text_color = shared.theme["light-fg"]
        bg_color = shared.theme["dark-fg"]
        if selected:
            text_color, bg_color = bg_color, text_color

        return shared.FONT.render(self.beauty_text, True, text_color, bg_color)


class CommandBar:
    """
    Lets you invoke commands in the editor

    Eg
    `:q -> quit`
    """

    # COLOR = "#701198"
    COLOR = "yellow4"

    def __init__(self) -> None:
        self._text = ""
        self.color = shared.theme["light-bg"]
        self.command_invalidated = False
        self.backspace_timer = Time(0.1)
        self.blink_timer = Time(0.5)
        self.cursors = itertools.cycle(("|", "_"))
        self.current_cursor = next(self.cursors)
        self.suggestion_surf: pygame.Surface | None = None
        self.original_commands: list[Command] = [
            Command((":q", ":quit"), self.on_quit),
            Command((":w", ":write"), soft_save_file),
            Command(":wq", self.on_save_exit),
            Command(":x", self.on_save_exit),
            Command((":save", ":saveas"), self.on_save_as),
            Command(
                ":theme",
                self.apply_selected_theme,
                subs=get_available_theme_names(),
            ),
            Command(":rel-no", exit, subs=["on", "off"]),
            Command((":rename", ":rn"), self.on_rename),
            Command(":reset-config", self.on_reset_config),
        ]
        self.commands = self.original_commands.copy()
        self.selected_command: Command | None = None
        self.rows = 1
        self._selected_col = 0
        self._selected_row = 0
        self.text_changed = False
        self.executed = False
        self.raised_subsidaries = False
        self.gen_blank_surf()

    def on_reset_config(self):
        reset_config()

    def on_save_as(self):
        self.on_rename()

    def on_save_exit(self):
        soft_save_file()
        exit()

    def on_rename(self):
        shared.naming_file = True
        shared.file_name = "|"

    @property
    def selected_col(self) -> int:
        return self._selected_col

    @selected_col.setter
    def selected_col(self, val: int):
        # max_col = (
        #     max(range(len(self.get_matched_commands())), key=lambda i: i // self.rows)
        #     / self.rows
        # )

        max_col = 0
        for i in range(len(self.get_matched_commands())):
            row = i % self.rows
            col = i // self.rows

            if row == self.selected_row:
                if col > max_col:
                    max_col = col

        if val > max_col:
            val = 0
        if val < 0:
            val = max_col

        self._selected_col = val
        self.draw_suggestions()
        if self.raised_subsidaries and hasattr(self.selected_command, "theme"):
            self.apply_selected_theme()

    @property
    def selected_row(self) -> int:
        return self._selected_row

    @selected_row.setter
    def selected_row(self, val: int):
        # max_row = max(
        #     range(len(self.get_matched_commands())), key=lambda i: i % self.rows
        # )

        max_row = 0
        for i in range(len(self.get_matched_commands())):
            row = i % self.rows
            col = i // self.rows

            if col == self.selected_col:
                if row > max_row:
                    max_row = row

        if val > max_row:
            val = 0
        if val < 0:
            val = max_row

        self._selected_row = val
        self.draw_suggestions()
        if self.raised_subsidaries and hasattr(self.selected_command, "theme"):
            self.apply_selected_theme()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, val: str) -> str:
        self._text = val
        self.text_changed = True
        if self.get_matched_commands():
            self.selected_col = 0
            self.selected_row = 0

    def on_quit(self):
        exit()

    def gen_blank_surf(self) -> None:
        self.surf = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT))

    def empty_command(self):
        self.color = shared.theme["light-bg"]
        self.text = ""
        self.command_invalidated = False
        self.commands = self.original_commands.copy()

    def on_backspace(self):
        self.current_cursor = "|"
        if not self.backspace_timer.tick():
            return
        if self.command_invalidated:
            self.empty_command()
            shared.typing_cmd = False
            return

        if not self.text:
            shared.typing_cmd = False
        else:
            self.text = self.text[:-1]

    def on_escape(self):
        self.empty_command()
        shared.typing_cmd = False

    def on_return(self):
        if self.command_invalidated:
            self.empty_command()
            shared.typing_cmd = False
            return

        self.update_commands()
        if not self.executed:
            self.text = f"Invalid Command '{self.text}'"
            self.color = shared.theme["select-bg"]
            self.command_invalidated = True
        elif not self.raised_subsidaries:
            shared.typing_cmd = False
            self.empty_command()

    def update_input(self):
        # Holding keys
        if shared.keys[pygame.K_BACKSPACE]:
            self.on_backspace()

        # On Release
        if shared.kr[pygame.K_BACKSPACE]:
            self.backspace_timer.reset()

        # Events
        for event in shared.events:
            if event.type == pygame.TEXTINPUT:
                if self.command_invalidated:
                    self.empty_command()
                self.text += event.text
                self.current_cursor = "_"
            elif event.type == pygame.VIDEORESIZE:
                self.gen_blank_surf()

        # One-Tap keys
        if shared.kp[pygame.K_RETURN]:
            self.on_return()
        elif shared.kp[pygame.K_ESCAPE]:
            self.on_escape()

    def update_cursor(self):
        if self.command_invalidated:
            self.current_cursor = ""
            return
        if self.blink_timer.tick():
            self.current_cursor = next(self.cursors)

    def execute_raise_subsidaries(self, command: Command):
        self.commands = [
            Command(":" + sub, command.callback, subsidary_cmd=True)
            for sub in command.subs
        ]
        self.raised_subsidaries = True
        self.text = f":{command.beauty_text} "
        self.draw_suggestions()

        # SPECIAL CASE !!!!
        if command.beauty_text == "theme":
            for command in self.commands:
                command.theme = True

    def apply_selected_theme(self):
        shared.config["theme"]["name"] = self.selected_command.beauty_text
        apply_theme(self.selected_command.beauty_text)
        self.draw_suggestions()
        write_config()

    def update_commands(self):
        matched_commands = self.get_matched_commands()
        for i, command in enumerate(matched_commands):
            row = i % self.rows
            col = i // self.rows

            selected = (row, col) == (self.selected_row, self.selected_col)
            if selected:
                self.executed = True
                if command.subs:
                    self.execute_raise_subsidaries(command)
                    return
                self.selected_command = command
                command.callback()
                self.raised_subsidaries = False
                return

        for command in self.commands:
            if command.is_perfect_match(self.text.strip()):
                self.executed = True
                if command.subs:
                    self.execute_raise_subsidaries(command)
                    return
                self.selected_command = command
                command.callback()
                self.raised_subsidaries = False

    def update_arrows(self):
        if not self.get_matched_commands():
            return
        if shared.kp[pygame.K_RIGHT]:
            self.selected_col += 1
        elif shared.kp[pygame.K_LEFT]:
            self.selected_col -= 1
        elif shared.kp[pygame.K_DOWN]:
            self.selected_row += 1
        elif shared.kp[pygame.K_UP]:
            self.selected_row -= 1

    def get_matched_commands(self) -> list[Command]:
        text = self.text
        if self.raised_subsidaries:
            text = self.text.split()
            if len(text) == 1:
                text = ""
            else:
                text = "" if not text else text[-1]
            text = ":" + text
        return [command for command in self.commands if command.is_match(text)]

    def draw_suggestions(self):
        matched_commands = self.get_matched_commands()

        if not matched_commands:
            self.suggestion_surf = None
            return

        PADDING = 10
        EACH_COMMAND_WIDTH = (
            len(
                max(
                    matched_commands, key=lambda command: len(command.beauty_text)
                ).beauty_text
            )
            * shared.FONT_WIDTH
        ) + PADDING
        EACH_COMMAND_HEIGHT = shared.FONT_HEIGHT

        COMMAND_SURF_WIDTH = shared.srect.width
        ROWS = calculate_number_of_rows(
            EACH_COMMAND_WIDTH,
            EACH_COMMAND_HEIGHT,
            len(matched_commands),
            COMMAND_SURF_WIDTH,
        )
        COMMAND_SURF_HEIGHT = ROWS * EACH_COMMAND_HEIGHT
        self.rows = ROWS

        self.suggestion_surf = pygame.Surface((COMMAND_SURF_WIDTH, COMMAND_SURF_HEIGHT))
        self.suggestion_surf.fill(shared.theme["dark-fg"])

        scroll = 0
        if ((self.selected_col + 1) * EACH_COMMAND_WIDTH) > COMMAND_SURF_WIDTH:
            scroll = self.selected_col + 1 - (COMMAND_SURF_WIDTH // EACH_COMMAND_WIDTH)
        for i, command in enumerate(matched_commands):
            row = i % ROWS
            col = i // ROWS

            selected = (row, col) == (self.selected_row, self.selected_col)
            if selected:
                self.selected_command = command
            cmd_surf = command.get_surf(selected)

            self.suggestion_surf.blit(
                cmd_surf,
                (EACH_COMMAND_WIDTH * (col - scroll), EACH_COMMAND_HEIGHT * row),
            )

    def update_suggestions(self):
        if self.command_invalidated or not self.text_changed:
            if self.command_invalidated:
                self.suggestion_surf = None
            return

        self.draw_suggestions()

    def update(self):
        if shared.selecting_file:
            return
        self.text_changed = False
        self.executed = False
        self.update_cursor()
        self.update_input()
        self.update_suggestions()
        self.update_arrows()

    def draw(self):
        if shared.selecting_file:
            return
        if shared.theme_changed:
            self.color = shared.theme["light-bg"]
            if self.command_invalidated:
                self.color = shared.theme["select-bg"]

        self.gen_blank_surf()
        self.surf.fill(self.color)

        text_surf = shared.FONT.render(
            self.text + self.current_cursor, True, shared.theme["default-fg"]
        )
        render_at(self.surf, text_surf, "midleft", (10, 0))

        if self.suggestion_surf is not None:
            temp = pygame.Surface(
                (
                    shared.srect.width,
                    self.surf.get_height() + self.suggestion_surf.get_height(),
                ),
                pygame.SRCALPHA,
            )
            render_at(temp, self.suggestion_surf, "topleft")
            render_at(temp, self.surf, "bottomleft")

            self.surf = temp
