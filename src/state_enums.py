from enum import Enum, StrEnum, auto


class State(Enum):
    EDITOR = auto()


class EditorState(StrEnum):
    INSERT = auto()
    SELECT = auto()
    NORMAL = auto()
