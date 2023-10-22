import pygame

from src import shared
from src.cursor import Cursor
from src.editor import Editor
from src.line_numbers import LineNumbers
from src.state_enums import State
from src.status_bar import StatusBar
from src.utils import render_at


class EditorState:
    def __init__(self) -> None:
        self.next_state: State | None = None
        self.editor = Editor()
        self.line_numbers = LineNumbers()
        self.status_bar = StatusBar()
        shared.cursor = Cursor()

        self.offset = 4

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
        self.handle_font_offset()
        self.editor.update()
        self.line_numbers.update()
        self.status_bar.update()
        shared.cursor.update()

    def draw_all(self):
        line_width, line_height = self.line_numbers.surf.get_size()
        editor_width, editor_height = self.editor.surf.get_size()
        status_width, status_height = self.status_bar.surf.get_size()

        render_at(shared.screen, self.line_numbers.surf, "topleft")
        render_at(shared.screen, self.editor.surf, "topleft", (line_width, 0))
        render_at(
            shared.screen,
            self.status_bar.surf,
            "bottomleft",
            (shared.FONT_WIDTH, -shared.FONT_WIDTH),
        )

    def draw(self):
        self.editor.draw()
        self.line_numbers.draw()
        self.status_bar.draw()
        shared.cursor.draw(self.editor.surf)
        self.draw_all()
