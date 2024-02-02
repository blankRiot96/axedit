import itertools

import pygame

from axedit import shared
from axedit.utils import Time, render_at


class CommandBar:
    """
    Lets you invoke commands in the editor

    Eg
    `:q -> quit`
    """

    def __init__(self) -> None:
        self.text = ""
        self.color = "yellow4"
        self.command_invalidated = False
        self.backspace_timer = Time(0.1)
        self.blink_timer = Time(0.5)
        self.cursors = itertools.cycle(("|", "_"))
        self.current_cursor = next(self.cursors)
        self.gen_blank_surf()

    def gen_blank_surf(self) -> None:
        self.surf = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT))

    def empty_command(self):
        self.color = "yellow4"
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
        if self.text in (":q", ":quit"):
            exit()
        else:
            self.text = f"Invalid Command '{self.text}'"
            self.color = "tomato"
            self.command_invalidated = True

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
        if self.blink_timer.tick():
            self.current_cursor = next(self.cursors)

    def update(self):
        self.update_cursor()
        self.update_input()

    def draw(self):
        self.surf.fill(self.color)

        text_surf = shared.FONT.render(self.text + self.current_cursor, True, "white")
        render_at(self.surf, text_surf, "midleft", (10, 0))
