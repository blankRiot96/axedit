import typing as t

from axedit.editor_state import EditorState
from axedit.enums import AppState
from axedit.internals import Internals


class StateLike(t.Protocol):
    def update(self): ...

    def draw(self): ...


class StateManager:
    def __init__(self, internals: Internals) -> None:
        self._internals = internals
        self.state_dict: dict[AppState, StateLike] = {
            AppState.EDITOR: EditorState,
        }

        self.state_obj: StateLike = self.state_dict.get(AppState.EDITOR)(
            self._internals
        )

    def update(self):
        self.state_obj.update()
        if self._internals.next_app_state is not None:
            self.state_obj = self.state_dict[self._internals.next_app_state](
                self._internals
            )

    def draw(self):
        self.state_obj.draw()
