from axedit.editor_interface import EditorInterface
from axedit.internals import Internals


class EditorState:
    """The text editing app state"""

    def __init__(self, internals: Internals) -> None:
        self._internals = internals
        self.interface = EditorInterface(self._internals)

    def update(self):
        self.interface.update()

    def draw(self):
        self.interface.draw()
