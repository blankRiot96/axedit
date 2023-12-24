from pathlib import Path

import pygame

from src import shared
from src.funcs import open_file
from src.state_enums import State
from src.utils import render_at


class Preview:
    def __init__(self) -> None:
        self.gen_blank()
        self.last_selected_index = 0
        self.padding = 5

    def gen_blank(self):
        self.surf = pygame.Surface(shared.srect.size)
        self.draw_line()

    def draw_line(self):
        pygame.draw.line(self.surf, "white", (0, 0), (0, self.surf.get_height()), 2)

    def regen_image(self):
        n_lines = shared.srect.height // shared.FONT_HEIGHT
        file = UI.file_tree.preview_files[UI.file_tree.selected_index]

        if file.is_dir():
            self.gen_blank()
            return
        with open(file) as f:
            lines = f.readlines()

        self.surf.fill("black")
        for y, line in enumerate(lines[:n_lines]):
            surf = shared.FONT.render(line, True, "white")
            self.surf.blit(
                surf, (self.padding, y * shared.FONT_HEIGHT, *surf.get_size())
            )

        self.draw_line()

    def update(self):
        if UI.file_tree.selected_index != self.last_selected_index:
            self.regen_image()

        self.last_selected_index = UI.file_tree.selected_index

    def draw(self):
        ...


class SearchBar:
    def __init__(self) -> None:
        self.surf = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT))
        self.icon_surf = shared.FONT.render("", True, "white")
        self.search_surf = shared.FONT.render("Search...", True, "grey")
        self.text = ""

    def update(self):
        ...

    def draw(self):
        self.surf.fill("black")
        render_at(self.surf, self.icon_surf, "topleft")
        if not self.text:
            render_at(
                self.surf,
                self.search_surf,
                "topleft",
                (self.icon_surf.get_width() + 10, 0),
            )
            return


class FileTree:
    def __init__(self) -> None:
        self.surf = pygame.Surface(shared.srect.size)
        self.current_path = Path(".")
        self.preview_files: list[Path] = list(self.current_path.iterdir())
        self.selected_index = 0
        self.scroll = 0

    def get_deco_name(self, index: int) -> str:
        file = self.preview_files[index]
        file_relative_path = file.__str__().replace("\\", "/")
        if file.is_dir():
            if self.preview_files[index + 1].parent.name == file.name:
                symbol = "-"
            else:
                symbol = "+"
            return f"[{symbol}] {file_relative_path}/"

        return f" F  {file_relative_path}"

    def collapse_preview(self) -> None:
        folder = self.preview_files[self.selected_index]
        for path in self.preview_files[:]:
            if path.parent.name == folder.name:
                self.preview_files.remove(path)

    def expand_preview(self) -> None:
        folder = self.preview_files[self.selected_index]

        if self.preview_files[self.selected_index + 1].parent.name == folder.name:
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

    def update(self):
        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_index += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_index -= 1

                elif event.key == pygame.K_RETURN:
                    file = self.preview_files[self.selected_index]
                    if file.is_dir():
                        self.expand_preview()
                    else:
                        open_file(self.preview_files[self.selected_index].__str__())
                        UI.state.next_state = State.EDITOR
        self.cap_selected_index()
        self.calc_scroll()

    def draw(self):
        self.surf.fill("black")
        for y, toplevel in enumerate(self.preview_files):
            anchor_pos = (y * shared.FONT_HEIGHT) + self.scroll
            if y == self.selected_index:
                rect = pygame.Rect(
                    0, anchor_pos, shared.srect.width, shared.FONT_HEIGHT
                )
                pygame.draw.rect(self.surf, "blue", rect)

            surf = shared.FONT.render(self.get_deco_name(y), True, "white")
            self.surf.blit(surf, (0, anchor_pos))


class FileSelectState:
    def __init__(self) -> None:
        self.next_state: State | None = None
        self.border_rect = shared.srect.scale_by(0.8, 0.8)
        self.surf = pygame.Surface(self.border_rect.size)

        UI.state = self
        UI.preview = Preview()
        UI.search_bar = SearchBar()
        UI.file_tree = FileTree()

    def update(self):
        UI.preview.update()
        UI.search_bar.update()
        UI.file_tree.update()

    def draw(self):
        UI.preview.draw()
        UI.file_tree.draw()
        UI.search_bar.draw()

        SB_HEIGHT = UI.search_bar.surf.get_height()

        self.surf = pygame.Surface(self.border_rect.size)
        render_at(self.surf, UI.search_bar.surf, "topleft", (10, 10))
        render_at(self.surf, UI.file_tree.surf, "topleft", (10, 20 + SB_HEIGHT))
        render_at(
            self.surf,
            UI.preview.surf,
            "topleft",
            (self.border_rect.width // 2, 20 + SB_HEIGHT),
        )
        pygame.draw.line(
            self.surf,
            "white",
            (0, SB_HEIGHT + 15),
            (self.border_rect.width, SB_HEIGHT + 15),
            width=2,
        )
        render_at(shared.screen, self.surf, "center")

        self.border_rect = shared.srect.scale_by(0.8, 0.8)
        pygame.draw.rect(shared.screen, "white", self.border_rect, 2, 20)


class UI:
    preview: Preview
    search_bar: SearchBar
    file_tree: FileTree
    state: FileSelectState
