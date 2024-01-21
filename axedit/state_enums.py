from enum import Enum, StrEnum, auto


class State(Enum):
    EDITOR = auto()
    FILE_SELECT = auto()
    MAIN_MENU = auto()


class FileState(StrEnum):
    WRITE = auto()
    SELECT = auto()
    NORMAL = auto()
