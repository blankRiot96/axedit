import typing as t

from axedit.editorstate import EditorState
from axedit.menu_state import MenuState
from axedit.state_enums import State


class StateLike(t.Protocol):
    next_state: State | None

    def update(self): ...

    def draw(self): ...


class StateManager:
    def __init__(self) -> None:
        self.state_dict: dict[State, StateLike] = {
            State.EDITOR: EditorState,
            State.MAIN_MENU: MenuState,
        }

        self.state_enum = State.MAIN_MENU
        self.state_obj: StateLike = self.state_dict.get(self.state_enum)()

    @property
    def state_enum(self) -> State:
        return self.__state_enum

    @state_enum.setter
    def state_enum(self, next_state: State) -> None:
        self.__state_enum = next_state
        self.state_obj: StateLike = self.state_dict.get(self.__state_enum)()

    def update(self):
        self.state_obj.update()
        if self.state_obj.next_state is not None:
            self.state_enum = self.state_obj.next_state

    def draw(self):
        self.state_obj.draw()
