import typing as t

import pygame

from axedit.editorstate import EditorState
from axedit.file_select_state import FileSelectState
from axedit.menu_state import MenuState
from axedit.state_enums import State


class StateLike(t.Protocol):
    next_state: State | None

    def update(self):
        ...

    def draw(self):
        ...


class StateManager:
    def __init__(self) -> None:
        self.state_dict: dict[State, StateLike] = {
            State.EDITOR: EditorState,
            State.FILE_SELECT: FileSelectState,
            State.MAIN_MENU: MenuState,
        }
        # self.songs = {
        #     State.MENU: "assets/audio/main-menu-bgm.wav",
        #     State.TUTORIAL: "assets/audio/game-bgm.wav",
        #     State.GAME: "assets/audio/game-bgm.wav",
        #     State.GAME_OVER: "assets/audio/game-over-bgm.wav",
        #     State.VICTORY: "assets/audio/victory-bgm.wav",
        # }
        self.state_enum = State.MAIN_MENU
        self.state_obj: StateLike = self.state_dict.get(self.state_enum)()

    @property
    def state_enum(self) -> State:
        return self.__state_enum

    @state_enum.setter
    def state_enum(self, next_state: State) -> None:
        self.__state_enum = next_state
        self.state_obj: StateLike = self.state_dict.get(self.__state_enum)()
        # pygame.mixer.music.load(self.songs[next_state])
        # pygame.mixer.music.play(fade_ms=2500, loops=-1)

    def update(self):
        self.state_obj.update()
        if self.state_obj.next_state is not None:
            self.state_enum = self.state_obj.next_state

    def draw(self):
        self.state_obj.draw()
