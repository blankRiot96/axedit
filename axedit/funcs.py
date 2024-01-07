import os
from pathlib import Path

import pygame

from axedit import shared


def is_event_frame(event_type: int) -> bool:
    for event in shared.events:
        if event.type == event_type:
            return True
    return False

def open_file(file: str) -> None:
    with open(file) as f:
        content = f.readlines()

    shared.cursor_pos = shared.Pos(0, 0)
    shared.file_name = file
    shared.chars = [list(line[:-1]) for line in content]
    if not shared.chars:
        shared.chars.append([])


def get_text():
    text = ""
    for row in shared.chars:
        text += "".join(row) + "\n"
    return text


def soft_save_file():
    with open(shared.file_name, "w") as f:
        f.write(get_text())


def save_file():
    if shared.file_name is None:
        return
    file = Path(shared.file_name)
    if file.exists():
        os.remove(file)
    soft_save_file()
