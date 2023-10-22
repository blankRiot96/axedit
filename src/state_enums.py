from enum import Enum, StrEnum, auto


class State(Enum):
    EDITOR = auto()


class EditorState(StrEnum):
    WRITE = auto()
    SELECT = auto()
    UI = auto()
    NORMAL = auto()
