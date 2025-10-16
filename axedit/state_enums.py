from enum import Enum, auto


class State(Enum):
    EDITOR = auto()
    FILE_SELECT = auto()
    MAIN_MENU = auto()


class FileState(Enum):
    INSERT = "insert"
    VISUAL = "visual"
    NORMAL = "normal"
