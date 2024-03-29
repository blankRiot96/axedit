import os

import pygame

from axedit import shared
from axedit.classes import CharList, Pos
from axedit.cursor import Cursor
from axedit.editor import Editor
from axedit.funcs import (
    offset_font_size,
    save_file,
    set_windows_title,
    soft_save_file,
    sync_file,
)
from axedit.line_numbers import LineNumbers
from axedit.logs import logger
from axedit.scrollbar import HorizontalScrollBar
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
        self.scrollbar = HorizontalScrollBar()
        self.last_file_time = 0

    def shared_reset(self):
        shared.chars_changed = True
        shared.action_str = ""
        shared.cursor_pos = Pos(0, 0)
        shared.saved = True
        shared.import_line_changed = False
        shared.cursor = Cursor()
        shared.action_queue.clear()
        shared.visual_mode_axis = Pos(0, 0)

    def on_ctrl_p(self):
        if shared.mode != FileState.NORMAL or shared.naming_file:
            return

        if shared.keys[pygame.K_LCTRL] and shared.kp[pygame.K_p]:
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

    def handle_font_offset(self):
        if not shared.keys[pygame.K_LCTRL]:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS:
                    offset_font_size(self.offset)
                elif event.key == pygame.K_MINUS:
                    offset_font_size(-self.offset)

    def push_action(self, action: str):
        shared.action_queue.append(action)
        shared.actions_modified = True

    def queue_actions(self):
        if shared.typing_cmd or shared.mode not in (FileState.NORMAL, FileState.VISUAL):
            return

        for event in shared.events:
            if event.type == pygame.TEXTINPUT:
                self.push_action(event.text)

        shared.action_str = "".join(shared.action_queue)

    def on_local_file_change(self):
        if os.stat(shared.file_name).st_mtime != self.last_file_time:
            sync_file(shared.file_name)
        self.last_file_time = os.stat(shared.file_name).st_mtime

    def update(self):
        if self.next_state is not None:
            return
        shared.chars_changed = False
        shared.actions_modified = False
        shared.font_offset = False
        self.on_local_file_change()
        self.char_handler()
        self.queue_actions()
        self.on_ctrl_p()
        self.on_ctrl_n()
        self.handle_font_offset()
        shared.cursor.update()
        self.editor.update()
        self.line_numbers.update()
        self.status_bar.update()
        self.on_ctrl_s()
        self.scrollbar.update()

    def char_handler(self):
        for i, lst in enumerate(shared.chars):
            if not isinstance(lst, CharList):
                shared.chars[i] = CharList(lst)

    def draw_all(self):
        line_width, line_height = self.line_numbers.surf.get_size()
        editor_width, editor_height = self.editor.surf.get_size()
        status_width, status_height = self.status_bar.surf.get_size()
        hor_scroll_width, hor_scroll_height = self.scrollbar.surf.get_size()

        self.scrollbar.zero_pos = line_width
        self.scrollbar.rect.y = (
            shared.srect.height - status_height - self.scrollbar.rect.height
        )

        render_at(shared.screen, self.line_numbers.surf, "topleft")
        render_at(
            shared.screen,
            self.editor.surf,
            "topleft",
            (line_width, 0),
        )
        render_at(
            shared.screen,
            self.status_bar.surf,
            "bottomleft",
        )

    def draw(self):
        self.editor.draw()
        shared.cursor.draw(self.editor.surf)
        if shared.chars_changed:
            shared.linter.update()
            self.editor.draw()
        self.line_numbers.draw()
        self.status_bar.draw()
        self.scrollbar.draw()
        self.draw_all()
