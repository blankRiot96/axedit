import itertools
import typing as t

import pygame

from axedit import shared
from axedit.utils import Time, render_at


def calculate_number_of_rows(
    cell_width, cell_height, total_cells, total_visible_width
) -> int:
    max_rows = 3
    total_width = cell_width * total_cells
    rows = 1 + (total_width // total_visible_width)

    return min(rows, max_rows)


class Command:
    def __init__(self, patterns: str | tuple[str], callback: t.Callable) -> None:
        self.patterns = patterns
        self.callback = callback
        self.beauty_text = self.get_beauty_text()

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
            return False

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
        text_color = "black"
        bg_color = "yellow4"
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
        self.color = CommandBar.COLOR
        self.command_invalidated = False
        self.backspace_timer = Time(0.1)
        self.blink_timer = Time(0.5)
        self.cursors = itertools.cycle(("|", "_"))
        self.current_cursor = next(self.cursors)
        self.suggestion_surf: pygame.Surface | None = None
        self.commands: list[Command] = [
            Command((":q", ":quit"), self.on_quit),
            Command((":w", ":write"), exit),
            Command(":wq", exit),
            Command(":x", exit),
            Command((":save", ":saveas"), exit),
            Command(":theme", exit),
            Command(":line-numbers", exit),
            Command(":cutee1", exit),
            Command(":cutee2", exit),
            Command(":cutee3", exit),
            Command(":cutee4", exit),
            Command(":cutee5", exit),
            Command(":cutee6", lambda: print("oniichan!!")),
            Command(":cutee7", exit),
            Command(":cutee8", exit),
            Command(":cutee9", exit),
            Command(":cutee10", exit),
            Command(":cutee11", exit),
            Command(":cutee12", exit),
            Command(":cutee13", exit),
            Command(":cutee14", exit),
            Command(":cutee15", exit),
            Command(":cutee16", exit),
            Command(":cutee17", exit),
            Command(":cutee18", exit),
            Command(":cutee19", exit),
            Command(":cutee20", exit),
            Command(":cutee21", exit),
        ]
        self.rows = 1
        self._selected_col = 0
        self._selected_row = 0
        self.text_changed = False
        self.executed = False
        self.gen_blank_surf()

    @property
    def selected_col(self) -> int:
        return self._selected_col

    @selected_col.setter
    def selected_col(self, val: int):
        max_col = (
            max(range(len(self.get_matched_commands())), key=lambda i: i // self.rows)
            / self.rows
        )

        if val > max_col:
            val = 0
        if val < 0:
            val = max_col
        self._selected_col = val
        self.draw_suggestions()

    @property
    def selected_row(self) -> int:
        return self._selected_row

    @selected_row.setter
    def selected_row(self, val: int):
        max_row = max(
            range(len(self.get_matched_commands())), key=lambda i: i % self.rows
        )

        if val > max_row:
            val = 0
        if val < 0:
            val = max_row

        self._selected_row = val
        self.draw_suggestions()

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
        self.color = CommandBar.COLOR
        self.text = ""
        self.command_invalidated = False

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
            self.color = "tomato"
            self.command_invalidated = True
        else:
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

    def update_commands(self):
        matched_commands = self.get_matched_commands()
        for i, command in enumerate(matched_commands):
            row = i % self.rows
            col = i // self.rows

            selected = (row, col) == (self.selected_row, self.selected_col)
            if selected:
                command.callback()
                self.executed = True
                return

        for command in self.commands:
            if command.is_perfect_match(self.text.strip()):
                self.executed = True
                command.callback()

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
        return [command for command in self.commands if command.is_match(self.text)]

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
        self.suggestion_surf.fill("yellow4")

        for i, command in enumerate(matched_commands):
            row = i % ROWS
            col = i // ROWS
            selected = (row, col) == (self.selected_row, self.selected_col)
            self.suggestion_surf.blit(
                command.get_surf(selected),
                (EACH_COMMAND_WIDTH * col, EACH_COMMAND_HEIGHT * row),
            )

    def update_suggestions(self):
        if self.command_invalidated or not self.text_changed:
            if self.command_invalidated:
                self.suggestion_surf = None
            return

        self.draw_suggestions()

    def update(self):
        self.text_changed = False
        self.executed = False
        self.update_cursor()
        self.update_input()
        self.update_suggestions()
        self.update_arrows()

    def draw(self):
        self.gen_blank_surf()
        self.surf.fill(self.color)

        text_surf = shared.FONT.render(self.text + self.current_cursor, True, "white")
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
