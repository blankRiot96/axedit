from itertools import cycle

import pygame

from axedit import shared
from axedit.classes import Pos
from axedit.funcs import get_text, is_event_frame, save_file
from axedit.input_queue import AcceleratedKeyPress, EventManager, InputManager
from axedit.logs import logger
from axedit.state_enums import FileState
from axedit.syntax_highlighting import apply_syntax_highlighting
from axedit.utils import Time


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
                pygame.K_TAB: self.on_tab,
            }
        )
        self.event_manager = EventManager({pygame.TEXTINPUT: self.on_write_char})
        self.accelerated_backspace = AcceleratedKeyPress(
            pygame.K_BACKSPACE, self.delete_chars
        )
        self.accelerated_new_line = AcceleratedKeyPress(pygame.K_RETURN, self.new_line)
        self.blink_timer = Time(0.5)
        self._typing = False

    def on_tab(self):
        if shared.autocompleting:
            return
        self.write_char(" " * 4)

    def on_esc(self):
        shared.mode = FileState.NORMAL
        shared.action_queue.clear()
        shared.action_str = ""
        if shared.cursor_pos.x > 0:
            shared.cursor_pos.x -= 1

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
            shared.cursor.cursor_visible = True

    def on_write_char(self, event):
        self.write_char(event.text)

    def write_char(self, text):
        for char in text:
            self.get_line().insert(shared.cursor_pos.x, char)
            shared.cursor_pos.x += 1

        closing_bracket = WriteMode.BRACKET_MATCHERS.get(text)
        if closing_bracket is not None:
            self.get_line().insert(shared.cursor_pos.x, closing_bracket)

        if char in "\"'":
            self.get_line().insert(shared.cursor_pos.x, char)
        self.typing = True
        shared.text_writing = True
        shared.saved = False

    def get_indentation_after_colon(self, line: list[str]) -> list[str]:
        count = 0

        str_line = "".join(line).strip()
        if str_line and str_line[-1] == ":":
            count = 4  # Starts off as 4 since we are adding a level of indendation
        for char in line:
            if char != " ":
                break
            count += 1

        return [" "] * count

    def new_line(self):
        if shared.autocompletion.completions:
            return

        line = self.get_line()

        # Pre line
        pre = line[: shared.cursor_pos.x]
        shared.chars[shared.cursor_pos.y] = pre

        # Update y pos
        shared.cursor_pos.y += 1

        # Post line
        post = self.get_indentation_after_colon(line) + line[shared.cursor_pos.x :]
        shared.chars.insert(shared.cursor_pos.y, post)

        # Update x pos
        shared.cursor_pos.x = 0
        # shared.cursor_pos.x = len(post)

        # Cleanup
        self.typing = True
        shared.saved = False

    def get_line(self):
        return shared.chars[shared.cursor_pos.y]

    def delete_chars(self):
        shared.cursor.cursor_visible = True
        if shared.cursor_pos.x == 0:
            if shared.cursor_pos.y == 0:
                return
            before_extension = len(shared.chars[shared.cursor_pos.y - 1])
            shared.chars[shared.cursor_pos.y - 1].extend(
                shared.chars[shared.cursor_pos.y]
            )
            self.go_prev_line()
            shared.cursor_pos.x = before_extension

            return

        line = "".join(self.get_line())
        if line and not line.strip():
            amount = len(line) % 4 or 4
            del shared.chars[shared.cursor_pos.y][-amount:]
            shared.cursor_pos.x -= amount
            return

        shared.saved = False
        self.typing = True

        shared.cursor_pos.x -= 1
        try:
            self.get_line().pop(shared.cursor_pos.x)
        except IndexError:
            return

    def go_prev_line(self):
        shared.chars.pop(shared.cursor_pos.y)
        shared.cursor_pos.y -= 1
        shared.cursor_pos.x = len(self.get_line())

    def handle_input(self):
        shared.text_writing = False
        self.input_manager.update()
        self.event_manager.update()
        self.accelerated_backspace.update()
        self.accelerated_new_line.update()
        self.blink_cursor()


class NormalMode:
    def __init__(self) -> None:
        self.input_manager = InputManager(
            {
                pygame.K_i: self.on_i,
                pygame.K_a: self.on_a,
                pygame.K_v: self.on_v,
                # pygame.K_f: self.on_f,
            }
        )
        self.event_manager = EventManager({pygame.TEXTINPUT: self.register_number})
        shared.naming_file = False
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
        shared.file_name = self.mini_cur
        shared.naming_file = True

    def on_a(self):
        shared.mode = FileState.INSERT
        shared.cursor_pos.x += 1
        shared.action_queue.clear()
        shared.action_str = ""

    def on_i(self):
        shared.mode = FileState.INSERT
        shared.action_queue.clear()
        shared.action_str = ""

    def on_v(self):
        shared.mode = FileState.VISUAL
        shared.visual_mode_axis = Pos(shared.cursor_pos.x, shared.cursor_pos.y)
        shared.action_queue.clear()
        shared.action_str = ""

    def name_file(self):
        if not shared.naming_file:
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
                    shared.naming_file = False
                elif event.key == pygame.K_BACKSPACE:
                    shared.file_name = shared.file_name[:-2]
                    shared.file_name += self.mini_cur

    def handle_input(self):
        self.name_file()
        shared.cursor.cursor_visible = True
        if shared.naming_file:
            return
        self.input_manager.update()
        self.event_manager.update()


class VisualMode:
    def __init__(self) -> None:
        self.event_manager = EventManager({pygame.TEXTINPUT: self.register_number})
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

    def handle_input(self) -> None:
        self.event_manager.update()
        if shared.kp[pygame.K_ESCAPE]:
            shared.mode = FileState.NORMAL
            shared.action_queue.clear()
            shared.action_str = ""


class Editor:
    def __init__(self) -> None:
        self.surf = pygame.Surface(
            (shared.srect.width, len(shared.chars) * shared.FONT_HEIGHT),
            pygame.SRCALPHA,
        )
        shared.scroll = pygame.Vector2()
        self.gen_image()

        self.input_handlers = {
            FileState.INSERT: WriteMode().handle_input,
            FileState.NORMAL: NormalMode().handle_input,
            FileState.VISUAL: VisualMode().handle_input,
        }
        self.stored_drag_pos: Pos = Pos(0, 0)
        self.first_drag = False

    def on_scroll(self):
        for event in shared.events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y < 0 and shared.scroll.y < -(
                    (len(shared.chars) - 7) * shared.FONT_HEIGHT
                ):
                    return
                shared.scroll.y += event.y * shared.FONT_HEIGHT
                shared.scroll.y = min(shared.scroll.y, 0)
                shared.chars_changed = True

    def gen_image(self):
        if shared.file_name is not None and shared.file_name.endswith(".py"):
            self.image = apply_syntax_highlighting()
        else:
            text = get_text()
            if text.strip() == "":
                text = ""
            self.image = shared.FONT.render(text, True, shared.theme["default-fg"])

    def handle_select_input(self): ...

    def handle_input(self):
        if shared.selecting_file:
            return
        input_handler = self.input_handlers[shared.mode]
        input_handler()

    def get_placement(self):
        x_pos = (
            shared.mouse_pos.x
            - (shared.FONT_WIDTH * shared.line_number_digits)
            + shared.scroll.x
        )
        y_pos = shared.mouse_pos.y - shared.scroll.y

        # Pixel to cursor pos
        x_pos /= shared.FONT_WIDTH
        y_pos /= shared.FONT_HEIGHT

        # Inting
        x_pos = int(x_pos)
        y_pos = int(y_pos)

        # Containing
        if y_pos > len(shared.chars) - 1:
            y_pos = len(shared.chars) - 1

        if x_pos > len(shared.chars[y_pos]) - 1:
            x_pos = len(shared.chars[y_pos])

        return Pos(x_pos, y_pos)

    def mouse_placement(self):
        if (
            shared.handling_scroll_bar
            or shared.selecting_file
            or shared.mouse_pos.y > shared.srect.height - shared.FONT_HEIGHT
        ):
            return
        for event in shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shared.cursor_pos = self.get_placement()

    def clear_queue(self):
        if shared.mode in (shared.FileState.NORMAL, shared.FileState.VISUAL):
            return

        shared.action_queue.clear()

    def on_drag(self) -> None:
        if (
            shared.handling_scroll_bar
            or shared.selecting_file
            or shared.mouse_pos.y > shared.srect.height - shared.FONT_HEIGHT
        ):
            return

        mouse_down = bool(shared.mouse_press[0])
        mouse_motion = is_event_frame(pygame.MOUSEMOTION)
        if not shared.mouse_press[0]:
            self.first_drag = False
            return

        if mouse_down and mouse_motion:
            if not self.first_drag:
                shared.visual_mode_axis = self.get_placement()
                self.first_drag = True
            shared.mode = FileState.VISUAL
            shared.cursor_pos = self.get_placement()

    def update(self):
        if shared.typing_cmd:
            return
        self.clear_queue()
        self.mouse_placement()
        self.on_scroll()
        self.handle_input()
        self.on_drag()
        if shared.file_name is not None and shared.file_name.endswith(".py"):
            shared.autocompletion.update()
            shared.linter.update()

    def draw(self):
        self.gen_image()
        self.surf = pygame.Surface(
            shared.srect.size,
            pygame.SRCALPHA,
        )

        is_python_file = shared.file_name is not None and shared.file_name.endswith(
            ".py"
        )
        self.surf.blit(
            self.image, (-shared.scroll.x, (not is_python_file) * shared.scroll.y)
        )
        if is_python_file:
            shared.autocompletion.draw(self.surf)
            shared.linter.draw(self.surf)
