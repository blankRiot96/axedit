from src import shared
from src.cursor import Cursor
from src.editor import Editor
from src.state_enums import State


class EditorState:
    def __init__(self) -> None:
        self.next_state: State | None = None
        self.editor = Editor()
        shared.cursor = Cursor()

    def update(self):
        self.editor.update()
        shared.cursor.update()

    def draw(self):
        self.editor.draw()
        shared.cursor.draw()
