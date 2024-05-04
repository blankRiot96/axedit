import itertools
from dataclasses import dataclass
from pathlib import Path

import pygame

from axedit import shared
from axedit.funcs import get_config_path, is_event_frame, open_file, set_windows_title
from axedit.input_queue import AcceleratedKeyPress
from axedit.logs import logger
from axedit.state_enums import State
from axedit.utils import Time, highlight_text, render_at


class Preview:
    def __init__(self) -> None:
        self.gen_blank()
        self.last_selected_file = 0
        self.padding = 5

    def gen_blank(self):
        self.surf = pygame.Surface(shared.srect.size, pygame.SRCALPHA)
        # self.surf.fill(shared.theme["default-bg"])
        self.draw_line()

    def draw_line(self):
        pygame.draw.line(
            self.surf,
            shared.theme["default-fg"],
            (0, 0),
            (0, self.surf.get_height()),
            2,
        )

    def get_lines(self, file: str | Path) -> list[str]:
        try:
            with open(file) as f:
                return f.readlines()
        except UnicodeDecodeError as e:
            return ["THIS FILE FORMAT IS NOT SUPPORTED BY THE EDITOR"]

    def regen_image(self):
        n_lines = shared.srect.height // shared.FONT_HEIGHT

        file = UI.file_tree.preview_files[UI.file_tree.selected_index]

        if file.is_dir():
            self.gen_blank()
            return

        lines = self.get_lines(file)

        self.gen_blank()
        for y, line in enumerate(lines[:n_lines]):
            surf = shared.FONT.render(line, True, shared.theme["default-fg"])
            self.surf.blit(
                surf, (self.padding, y * shared.FONT_HEIGHT, *surf.get_size())
            )

        self.draw_line()

    def update(self):
        # if not UI.file_tree.preview_files:
        #     self.gen_blank()
        #     return
        # file = UI.file_tree.preview_files[UI.file_tree.selected_index]

        # if file != self.last_selected_file:
        #     self.regen_image()

        # self.last_selected_file = file
        ...

    def draw(self):
        if not UI.file_tree.preview_files:
            self.gen_blank()
            return
        file = UI.file_tree.preview_files[UI.file_tree.selected_index]

        if file != self.last_selected_file:
            self.regen_image()

        self.last_selected_file = file


class SearchBar:
    BAR = "|"

    def __init__(self) -> None:
        self.gen_blank()
        self.icon_surf = shared.FONT.render("", True, shared.theme["default-fg"])
        self.search_surf = shared.FONT.render(
            "Search...", True, shared.theme["default-fg"]
        )
        self.text = ""
        self.cursors = itertools.cycle(("", SearchBar.BAR))
        self.cursor = next(self.cursors)
        self.blink_timer = Time(0.7)

        self.accel = AcceleratedKeyPress(pygame.K_BACKSPACE, self.on_delete)
        self.start_filtering = False

    def gen_blank(self):
        self.surf = pygame.Surface(
            (shared.srect.width, shared.FONT_HEIGHT), pygame.SRCALPHA
        )

    def on_delete(self):
        self.text = self.text[:-1]
        self.blink_timer.reset()
        self.cursor = SearchBar.BAR

        if self.text:
            UI.file_tree.matches = []
            UI.file_tree.seq = Path(".").rglob("*")
            self.start_filtering = True
        else:
            UI.file_tree.reset_preview_files()

    def on_enter(self, event):
        self.text += event.text
        self.blink_timer.reset()
        self.cursor = SearchBar.BAR
        UI.file_tree.matches = []
        UI.file_tree.seq = Path(".").rglob("*")

        self.start_filtering = True

    def update(self):
        if self.text and self.start_filtering:
            UI.file_tree.filter_preview_files()
        self.accel.update()
        for event in shared.events:
            if event.type == pygame.TEXTINPUT:
                self.on_enter(event)

        if self.blink_timer.tick():
            self.cursor = next(self.cursors)

    def draw(self):
        self.gen_blank()
        render_at(self.surf, self.icon_surf, "topleft")
        icon_offset = (self.icon_surf.get_width() + 10, 0)
        if not self.text:
            render_at(
                self.surf,
                self.search_surf,
                "topleft",
                icon_offset,
            )
            return

        text_surf = shared.FONT.render(
            self.text + self.cursor, True, shared.theme["default-fg"]
        )
        render_at(self.surf, text_surf, "topleft", icon_offset)


@dataclass
class Match:
    file: Path
    matched_indeces: list[int]


class FileTree:
    def __init__(self) -> None:
        self.gen_blank()
        self.current_path = Path(".")
        self.preview_files: list[Path] = list(self.current_path.iterdir())
        self.original_preview_files = self.preview_files.copy()
        self.selected_index = 0
        self.scroll = 0
        self.matches = []

    def gen_blank(self):
        self.surf = pygame.Surface(shared.srect.size, pygame.SRCALPHA)

    def get_deco_name(self, index: int) -> str:
        file = self.preview_files[index]
        file_relative_path = file.__str__().replace("\\", "/")
        if file.is_dir():
            if index > len(self.preview_files) - 2:
                symbol = "+"
            elif self.preview_files[index + 1].parent.name == file.name:
                symbol = "-"
            else:
                symbol = "+"
            return f"[{symbol}] {file_relative_path}/"

        return f" F  {file_relative_path}"

    def collapse_preview(self) -> None:
        if UI.search_bar.text:
            return
        folder = self.preview_files[self.selected_index]
        for path in self.preview_files[:]:
            if path.parent.name == folder.name:
                self.preview_files.remove(path)

    def expand_preview(self) -> None:
        folder = self.preview_files[self.selected_index]

        last_preview_file = self.selected_index + 1 == len(self.preview_files)
        if (
            not last_preview_file
            and self.preview_files[self.selected_index + 1].parent.name == folder.name
        ):
            self.collapse_preview()
            return

        for i, path in enumerate(folder.iterdir(), start=1):
            self.preview_files.insert(self.selected_index + i, path)

    def cap_selected_index(self):
        n_preview_files = len(UI.file_tree.preview_files)
        if self.selected_index >= n_preview_files:
            self.selected_index = 0

        elif self.selected_index < 0:
            self.selected_index = n_preview_files - 1

    def calc_scroll(self):
        if self.selected_index > 6:
            self.scroll = -(shared.FONT_HEIGHT * (self.selected_index - 6))
        else:
            self.scroll = 0

    def enter_editor(self):
        try:
            open_file(self.preview_files[self.selected_index].__str__())
        except UnicodeDecodeError:
            return
        shared.editing_config_file = (
            self.preview_files[self.selected_index] == get_config_path()
        )
        UI.state.next_state = State.EDITOR
        set_windows_title()

    def on_enter(self):
        try:
            file = self.preview_files[self.selected_index]
        except IndexError:
            # UI.preview.gen_blank()
            return

        if file.is_dir():
            self.expand_preview()
        else:
            self.enter_editor()

    def update(self):
        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_index += 1
                elif event.key == pygame.K_UP:
                    self.selected_index -= 1

                elif event.key == pygame.K_RETURN:
                    self.on_enter()

                elif event.key == pygame.K_ESCAPE:
                    shared.selecting_file = False

        self.cap_selected_index()
        self.calc_scroll()

    def reset_preview_files(self):
        self.preview_files = self.original_preview_files.copy()

    def render_unfiltered_preview_files(self):
        limit = (
            int(UI.state.border_rect.height / shared.FONT_HEIGHT) + 2
        )  # +2 just in case
        scroll = int(-self.scroll / shared.FONT_HEIGHT)
        for y, toplevel in enumerate(self.preview_files[scroll : scroll + limit]):
            y += scroll
            anchor_pos = (y * shared.FONT_HEIGHT) + self.scroll
            rect = pygame.Rect(
                0, anchor_pos, UI.state.border_rect.width // 2, shared.FONT_HEIGHT
            )

            if y == self.selected_index:
                pygame.draw.rect(self.surf, (100, 100, 255), rect)

            surf = shared.FONT.render(
                self.get_deco_name(y), True, shared.theme["default-fg"]
            )
            rect.y = 0
            if rect.width < surf.get_width():
                surf = surf.subsurface(rect).copy()
            self.surf.blit(surf, (0, anchor_pos))

    def get_match_indeces(self, file_name: str) -> list[int] | None:
        # UI.file_tree.selected_index = 0
        search_text = UI.search_bar.text
        text = itertools.cycle(search_text)
        current_search_char = next(text)
        passers = []
        for index, char in enumerate(file_name):
            if char == current_search_char:
                passers.append(index)
                if len(passers) == len(search_text):
                    break
                current_search_char = next(text)

        if len(passers) == len(search_text):
            return passers

        return None

    def get_matches(self):
        for _ in range(10):
            try:
                file = next(self.seq)
            except StopIteration:
                UI.search_bar.start_filtering = False
                self.matches.sort(key=lambda x: x.matched_indeces)
                return
            match_indeces = self.get_match_indeces(file.__str__().replace("\\", "/"))
            if match_indeces is None:
                continue

            self.matches.append(Match(file, match_indeces))

        self.matches.sort(key=lambda x: x.matched_indeces)

    def filter_preview_files(self):
        """Matches preview files to the text typed in search bar"""

        self.get_matches()
        self.preview_files = [match.file for match in self.matches]

    def render_filtered_preview_files(self):
        limit = (
            int(UI.state.border_rect.height / shared.FONT_HEIGHT) + 2
        )  # +2 just in case

        scroll = int(-self.scroll / shared.FONT_HEIGHT)
        for y, match in enumerate(self.matches[scroll : scroll + limit]):
            y += scroll
            anchor_pos = (y * shared.FONT_HEIGHT) + self.scroll
            rect = pygame.Rect(
                0, anchor_pos, UI.state.border_rect.width // 2, shared.FONT_HEIGHT
            )
            if y == self.selected_index:
                pygame.draw.rect(self.surf, (100, 100, 255), rect)

            offseted_match_indeces = [index + 4 for index in match.matched_indeces]
            surf = highlight_text(
                shared.FONT,
                self.get_deco_name(y),
                True,
                shared.theme["default-fg"],
                offseted_match_indeces,
                shared.theme["keyword"],
            )
            rect.y = 0
            if rect.width < surf.get_width():
                surf = surf.subsurface(rect).copy()
            self.surf.blit(surf, (0, anchor_pos))

    def draw(self):
        self.gen_blank()
        if UI.search_bar.text:
            self.render_filtered_preview_files()
            return
        self.render_unfiltered_preview_files()


class FileSelector:
    def __init__(self) -> None:
        self.next_state: State | None = None
        self.border_rect = shared.srect.scale_by(0.8, 0.8)
        self.surf = pygame.Surface(self.border_rect.size, pygame.SRCALPHA)

        UI.state = self
        UI.preview = Preview()
        UI.search_bar = SearchBar()
        UI.file_tree = FileTree()
        self.create_glassy()

    def create_glassy(self):
        self.glassy_surf = pygame.Surface(self.border_rect.size, pygame.SRCALPHA)
        self.glassy_surf.fill(shared.theme["default-bg"])
        self.glassy_surf.set_alpha(230)

    def update(self):
        if is_event_frame(pygame.VIDEORESIZE):
            self.create_glassy()
        UI.preview.update()
        UI.search_bar.update()
        UI.file_tree.update()

    def draw(self):
        UI.preview.draw()
        UI.file_tree.draw()
        UI.search_bar.draw()

        SB_HEIGHT = UI.search_bar.surf.get_height()

        self.surf = pygame.Surface(self.border_rect.size, pygame.SRCALPHA)
        self.surf.blit(self.glassy_surf, (0, 0))
        render_at(self.surf, UI.search_bar.surf, "topleft", (10, 10))
        render_at(self.surf, UI.file_tree.surf, "topleft", (0, 20 + SB_HEIGHT))
        render_at(
            self.surf,
            UI.preview.surf,
            "topleft",
            (self.border_rect.width // 2, 20 + SB_HEIGHT),
        )
        pygame.draw.line(
            self.surf,
            shared.theme["default-fg"],
            (0, SB_HEIGHT + 15),
            (self.border_rect.width, SB_HEIGHT + 15),
            width=2,
        )
        render_at(shared.screen, self.surf, "center")

        self.border_rect = shared.srect.scale_by(0.8, 0.8)
        pygame.draw.rect(shared.screen, shared.theme["default-fg"], self.border_rect, 2)


class UI:
    preview: Preview
    search_bar: SearchBar
    file_tree: FileTree
    state: FileSelector
