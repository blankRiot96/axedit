import os
from itertools import cycle

import pygame

from src import shared
from src.autocompletions import AutoCompletions
from src.funcs import get_text, save_file
from src.state_enums import FileState
from src.syntax_highlighting import apply_syntax_highlighting
from src.utils import AcceleratedKeyPress, EventManager, InputManager, Time


class WriteMode:
    BRACKET_MATCHERS = {
        "(": ")",
        "[": "]",
        "{": "}",
    }

    def __init__(self) -> None:
        self.input_manager = InputManager(
            {
                pygame.K_ESCAPE: self.on_esc,
                pygame.K_TAB: lambda: self.write_char(" " * 4),
            }
        )
        self.event_manager = EventManager({pygame.TEXTINPUT: self.on_write_char})
        self.accelerated_backspace = AcceleratedKeyPress(
            pygame.K_BACKSPACE, self.delete_chars
        )
        self.accelerated_new_line = AcceleratedKeyPress(pygame.K_RETURN, self.new_line)
        self.blink_timer = Time(0.5)
        self._typing = False

    def on_esc(self):
        shared.mode = FileState.NORMAL

    @property
    def typing(self) -> bool:
        return self._typing

    @typing.setter
    def typing(self, val):
        self._typing = val
        self.blink_timer.reset()

    def blink_cursor(self):
        if self.typing and self.blink_timer.tick():
            self.typing = False

        if self.typing:
            shared.cursor.alpha = 255

    def on_write_char(self, event):
        self.write_char(event.text)

    def write_char(self, text):
        for char in text:
            self.get_line().insert(shared.cursor_pos.x, char)
            shared.cursor_pos.x += 1

        closing_bracket = WriteMode.BRACKET_MATCHERS.get(text)
        if closing_bracket is not None:
            self.get_line().insert(shared.cursor_pos.x, closing_bracket)
        self.typing = True
        shared.text_writing = True

    def new_line(self):
        if shared.autocompleting:
            return

        line = self.get_line()
        pre = line[: shared.cursor_pos.x]
        shared.chars[shared.cursor_pos.y] = pre
        post = line[shared.cursor_pos.x :]

        shared.chars.insert(shared.cursor_pos.y + 1, post)
        shared.cursor_pos.y += 1
        shared.cursor_pos.x = 0
        self.typing = True

    def get_line(self):
        return shared.chars[shared.cursor_pos.y]

    def delete_chars(self):
        if shared.cursor_pos.x == 0:
            if shared.cursor_pos.y == 0:
                return
            shared.chars[shared.cursor_pos.y - 1].extend(
                shared.chars[shared.cursor_pos.y]
            )
            self.go_prev_line()

            return

        line = "".join(self.get_line())
        if not line.strip():
            shared.chars[shared.cursor_pos.y] = []
            shared.cursor_pos.x = 0
            if shared.cursor_pos.y == 0:
                return
            self.go_prev_line()
            return

        shared.cursor_pos.x -= 1
        self.get_line().pop(shared.cursor_pos.x)
        self.typing = True

    def go_prev_line(self):
        shared.chars.pop(shared.cursor_pos.y)
        shared.cursor_pos.y -= 1
        shared.cursor_pos.x = len(self.get_line())

    def handle_input(self):
        shared.text_writing = False
        self.input_manager.update(shared.events)
        self.event_manager.update(shared.events)
        self.accelerated_backspace.update(shared.events, shared.keys)
        self.accelerated_new_line.update(shared.events, shared.keys)
        self.blink_cursor()


class NormalMode:
    def __init__(self) -> None:
        self.input_manager = InputManager(
            {
                pygame.K_q: self.on_q,
                pygame.K_w: self.on_w,
                pygame.K_e: self.on_e,
                # pygame.K_s: self.on_s,
                pygame.K_f: self.on_f,
            }
        )
        self.event_manager = EventManager({pygame.TEXTINPUT: self.register_number})
        self.naming_file = False
        self.mini_curs = cycle(("|", "_"))
        self.mini_timer = Time(0.5)
        self.mini_cur = "_"

        self.registering_number = False

    def register_number(self, event: pygame.Event):
        if event.text.isdigit():
            if self.registering_number:
                shared.registered_number = int(
                    f"{shared.registered_number}{event.text}"
                )
            else:
                shared.registered_number = int(event.text)
            self.registering_number = True
        else:
            self.registering_number = False

    def on_f(self):
        if shared.file_name is not None:
            os.remove(shared.file_name)
        shared.file_name = self.mini_cur
        self.naming_file = True

    def on_w(self):
        shared.mode = FileState.WRITE

    def on_s(self):
        shared.mode = FileState.SELECT

    def on_q(self):
        shared.cursor_pos.x, shared.cursor_pos.y = 0, 0

    def on_e(self):
        shared.cursor_pos.y = len(shared.chars) - 1
        shared.cursor_pos.x = len(shared.chars[-1])

    def name_file(self):
        if not self.naming_file:
            return

        if self.mini_timer.tick():
            self.mini_cur = next(self.mini_curs)
            shared.file_name = shared.file_name[:-1] + self.mini_cur

        for event in shared.events:
            if event.type == pygame.TEXTINPUT:
                shared.file_name = shared.file_name[:-1]
                shared.file_name += event.text
                shared.file_name += self.mini_cur
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    shared.file_name = shared.file_name[:-1]
                    save_file()
                    self.naming_file = False
                elif event.key == pygame.K_BACKSPACE:
                    shared.file_name = shared.file_name[:-2]
                    shared.file_name += self.mini_cur

    def handle_input(self):
        self.name_file()
        shared.cursor.alpha = 255
        if self.naming_file:
            return
        self.input_manager.update(shared.events)
        self.event_manager.update(shared.events)


class Editor:
    def __init__(self) -> None:
        self.surf = pygame.Surface(
            (shared.srect.width, len(shared.chars) * shared.FONT_HEIGHT),
            pygame.SRCALPHA,
        )
        self.pre_rendered_lines: list[pygame.Surface] = [None for _ in shared.chars]
        self.gen_image()
        self.offset = pygame.Vector2()

        self.input_handlers = {
            FileState.WRITE: WriteMode().handle_input,
            FileState.NORMAL: NormalMode().handle_input,
            FileState.SELECT: self.handle_select_input,
        }
        self.autocompletion = AutoCompletions()

    def on_scroll(self):
        for event in shared.events:
            if event.type == pygame.MOUSEWHEEL:
                self.offset.y += event.y * 30
                self.offset.y = min(self.offset.y, 0)

    def gen_image(self):
        if shared.file_name is not None and shared.file_name.endswith(".py"):
            self.image = apply_syntax_highlighting(self.pre_rendered_lines)
        else:
            text = get_text()
            if text.strip() == "":
                text = ""
            self.image = shared.FONT.render(text, True, "white")

    def handle_select_input(self):
        ...

    def handle_input(self):
        input_handler = self.input_handlers[shared.mode]
        input_handler()

    def pre_render_lines(self):
        surfs = self.pre_rendered_lines.copy()
        self.pre_rendered_lines = []
        for y in range(len(shared.chars)):
            if y < len(surfs) and surfs[y] is not None:
                self.pre_rendered_lines.append(surfs[y])
                continue
            self.pre_rendered_lines.append(None)

    def update(self):
        # TODO: Figure this out - You can do it!
        self.pre_render_lines()
        self.handle_input()
        self.autocompletion.update()
        self.gen_image()
        self.on_scroll()

    def draw(self):
        self.surf = pygame.Surface(
            (shared.srect.width, len(shared.chars) * shared.FONT_HEIGHT),
            pygame.SRCALPHA,
        )
        self.surf.blit(self.image, (0, 0))
        self.autocompletion.draw(self.surf)
