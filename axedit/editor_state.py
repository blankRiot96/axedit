from axedit.internals import Internals


class EditorState:
    def __init__(self, internals: Internals) -> None:
        self._internals = internals

    def update(self):
        pass

    def draw(self):
        pass
