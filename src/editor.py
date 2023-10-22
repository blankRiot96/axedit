import pygame

from src import shared
from src.utils import EventManager, InputManager, KeyManager, Time


class Editor:
    def __init__(self) -> None:
        self.surf = pygame.Surface(shared.srect.size, pygame.SRCALPHA)
        self.gen_image()
        self.blink_timer = Time(0.5)
        self._typing = False
        self.input_manager = InputManager(
            {
                pygame.K_RETURN: self.new_line,
                pygame.K_BACKSPACE: self.delete_single_char,
                pygame.K_TAB: lambda: self.write_char(" " * 4),
            }
        )
        self.event_manager = EventManager({pygame.TEXTINPUT: self.on_write_char})
        self.key_manager = KeyManager({pygame.K_BACKSPACE: self.delete_chars})
        self.delete_timer = Time(0.5)

    def gen_image(self):
        text = self.get_text()
        if text.strip() == "":
            text = ""
        self.image = shared.FONT.render(text, True, "white")

    @property
    def typing(self) -> bool:
        return self._typing

    @typing.setter
    def typing(self, val):
        self._typing = val
        self.blink_timer.reset()

    def get_text(self):
        text = ""
        for row in shared.chars:
            text += "".join(row) + "\n"
        return text

    def blink_cursor(self):
        if self.typing and self.blink_timer.tick():
            self.typing = False

        if self.typing:
            shared.cursor.alpha = 255

    def handle_input(self):
        self.input_manager.update(shared.events)
        self.event_manager.update(shared.events)

        if self.delete_timer.tick():
            self.key_manager.update(shared.keys)
            if self.delete_timer.time_to_pass <= 0.02:
                self.delete_timer.time_to_pass = 0.02
                return
            self.delete_timer.time_to_pass -= 0.3

    def on_write_char(self, event):
        self.write_char(event.text)

    def write_char(self, text):
        for char in text:
            self.get_line().insert(shared.cursor_pos.x, char)
            shared.cursor_pos.x += 1
            self.typing = True

    def new_line(self):
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
        if not "".join(self.get_line()).strip():
            if shared.cursor_pos.y == 0:
                return
            self.go_prev_line()
            return

        if shared.cursor_pos.x == 0:
            shared.chars[shared.cursor_pos.y - 1].extend(
                shared.chars[shared.cursor_pos.y]
            )
            self.go_prev_line()

            return
        shared.cursor_pos.x -= 1
        self.get_line().pop(shared.cursor_pos.x)
        self.typing = True

    def go_prev_line(self):
        shared.chars.pop(shared.cursor_pos.y)
        shared.cursor_pos.y -= 1
        shared.cursor_pos.x = len(self.get_line())

    def delete_single_char(self):
        self.delete_chars()
        self.delete_timer.reset()
        self.delete_timer.time_to_pass = 0.5

    def update(self):
        self.handle_input()
        self.blink_cursor()
        self.gen_image()

    def draw(self):
        self.surf.fill("black")
        self.surf.blit(self.image, (0, 0))
