from axedit.internals import Internals


class EditorInterface:
    """Processes and translates the human input(mouse and key press) to text editing actions"""

    def __init__(self, internals: Internals) -> None:
        self._internals = internals

    def update(self):
        pass

    def draw(self):
        pass
