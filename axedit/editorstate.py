import pygame

from axedit import shared
from axedit.classes import CharList, Pos
from axedit.cursor import Cursor
from axedit.editor import Editor
from axedit.funcs import offset_font_size, save_file, set_windows_title, soft_save_file
from axedit.line_numbers import LineNumbers
from axedit.state_enums import FileState, State
from axedit.status_bar import StatusBar
from axedit.utils import render_at

shared.chars = CharList([CharList([])])


class EditorState:
    def __init__(self) -> None:
        self.shared_reset()
        self.next_state: State | None = None
        self.editor = Editor()
        self.line_numbers = LineNumbers()
        self.status_bar = StatusBar()
        self.offset = 4

    def shared_reset(self):
        shared.cursor_pos = Pos(0, 0)
        shared.saved = True
        shared.import_line_changed = False
        shared.cursor = Cursor()

    def on_ctrl_p(self):
        if shared.mode != FileState.NORMAL or shared.naming_file:
            return

        if not shared.keys[pygame.K_LCTRL]:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                save_file()
                self.next_state = State.FILE_SELECT

    def on_ctrl_n(self):
        if shared.mode != FileState.NORMAL:
            return

        if not shared.keys[pygame.K_LCTRL]:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                shared.file_name = None
                shared.chars = CharList([[""]])
                self.next_state = State.EDITOR
                set_windows_title()

    def on_ctrl_s(self):
        if not shared.keys[pygame.K_LCTRL]:
            return
        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                soft_save_file()
                shared.saved = True

    def handle_font_offset(self):
        if not shared.keys[pygame.K_LCTRL]:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS:
                    offset_font_size(self.offset)
                elif event.key == pygame.K_MINUS:
                    offset_font_size(-self.offset)

    def update(self):
        self.char_handler()
        self.on_ctrl_p()
        self.on_ctrl_n()
        if self.next_state is not None:
            return
        self.handle_font_offset()
        self.editor.update()
        self.line_numbers.update()
        self.status_bar.update()
        shared.cursor.update()
        self.on_ctrl_s()

    def char_handler(self):
        shared.chars_changed = False
        for i, lst in enumerate(shared.chars):
            if not isinstance(lst, CharList):
                shared.chars[i] = CharList(lst)

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
