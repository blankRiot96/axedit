from enum import Enum, StrEnum, auto


class State(Enum):
    EDITOR = auto()
    FILE_SELECT = auto()


class FileState(StrEnum):
    WRITE = auto()
    SELECT = auto()
    NORMAL = auto()