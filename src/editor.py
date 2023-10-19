import pygame

from src import shared
from src.utils import EventManager, InputManager, KeyManager, Time


class Editor:
    def __init__(self) -> None:
        self.chars = []
        self.image = shared.FONT.render("".join(self.chars), True, "white")
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

    @property
    def typing(self) -> bool:
        return self._typing

    @typing.setter
    def typing(self, val):
        self._typing = val
        self.blink_timer.reset()

    def update(self):
        self.handle_input()
        self.blink_cursor()

        self.image = shared.FONT.render("".join(self.chars), True, "white")

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
            self.chars.append(char)
            shared.cursor_pos.x += 1
            self.typing = True

    def new_line(self):
        self.chars.append("\n")
        shared.cursor_pos.y += 1
        shared.cursor_pos.x = 0
        self.typing = True

    def get_line(self):
        if "\n" not in self.chars:
            return self.chars
        line_start = "".join(self.chars).rfind("\n") + 1
        return self.chars[line_start:]

    def delete_chars(self):
        if not self.chars:
            return
        char = self.chars.pop()
        if char == "\n":
            shared.cursor_pos.y -= 1
            shared.cursor_pos.x = len(self.get_line()) + 1
        shared.cursor_pos.x -= 1
        self.typing = True

    def delete_single_char(self):
        self.delete_chars()
        self.delete_timer.reset()
        self.delete_timer.time_to_pass = 0.5

    def draw(self):
        shared.screen.blit(self.image, (0, 0))
