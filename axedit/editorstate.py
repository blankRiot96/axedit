import pygame

from axedit import shared
from axedit.cursor import Cursor
from axedit.editor import Editor
from axedit.funcs import save_file, soft_save_file
from axedit.line_numbers import LineNumbers
from axedit.state_enums import FileState, State
from axedit.status_bar import StatusBar
from axedit.utils import render_at


class EditorState:
    def __init__(self) -> None:
        shared.saved = True
        self.next_state: State | None = None
        self.editor = Editor()
        self.line_numbers = LineNumbers()
        self.status_bar = StatusBar()
        shared.cursor = Cursor()

        self.offset = 4

    def on_o(self):
        if shared.mode != FileState.NORMAL or shared.naming_file:
            return
        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                save_file()
                self.next_state = State.FILE_SELECT

    def on_n(self):
        if shared.mode != FileState.NORMAL:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                shared.file_name = None
                shared.chars = [[""]]
                self.next_state = State.EDITOR

    def on_ctrl_s(self):
        if not shared.keys[pygame.K_LCTRL]:
            return
        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                soft_save_file()
                shared.saved = True

    def offset_font_size(self, offset: int):
        shared.font_size += offset
        shared.FONT = pygame.font.Font(shared.FONT_PATH, shared.font_size)
        shared.FONT_WIDTH = shared.FONT.render("w", True, "white").get_width()
        shared.FONT_HEIGHT = shared.FONT.get_height()
        shared.cursor.gen_image()

    def handle_font_offset(self):
        if not shared.keys[pygame.K_LCTRL]:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS:
                    self.offset_font_size(self.offset)
                elif event.key == pygame.K_MINUS:
                    self.offset_font_size(-self.offset)

    def update(self):
        self.on_o()
        self.on_n()
        if self.next_state is not None:
            return
        self.handle_font_offset()
        self.editor.update()
        self.line_numbers.update()
        self.status_bar.update()
        shared.cursor.update()
        self.on_ctrl_s()

    def draw_all(self):
        line_width, line_height = self.line_numbers.surf.get_size()
        editor_width, editor_height = self.editor.surf.get_size()
        status_width, status_height = self.status_bar.surf.get_size()

        render_at(shared.screen, self.line_numbers.surf, "topleft", self.editor.offset)
        render_at(
            shared.screen,
            self.editor.surf,
            "topleft",
            (line_width, 0) + self.editor.offset,
        )
        render_at(
            shared.screen,
            self.status_bar.surf,
            "bottomleft",
        )

    def draw(self):
        self.editor.draw()
        self.line_numbers.draw()
        self.status_bar.draw()
        shared.cursor.draw(self.editor.surf)
        self.draw_all()
