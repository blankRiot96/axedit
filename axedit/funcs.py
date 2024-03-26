import os
import platform
import typing as t
from pathlib import Path

import pygame

from axedit import shared
from axedit.classes import CharList, Pos


def safe_close_connections() -> None:
    """Safely close autocompletion and linting servers"""
    if hasattr(shared, "autocompletion"):
        shared.autocompletion.close_connections()
    if hasattr(shared, "linter"):
        shared.linter.close_connections()


def open_file(file: str) -> None:
    with open(file) as f:
        content = f.readlines()

    shared.cursor_pos = Pos(0, 0)
    shared.file_name = file
    shared.chars = CharList([list(line[:-1]) for line in content])
    if not shared.chars:
        shared.chars.append([])


def soft_save_file():
    shared.saved = True
    if shared.file_name is None:
        return
    with open(shared.file_name, "w") as f:
        f.write(get_text())


def save_file():
    if shared.file_name is None:
        return
    file = Path(shared.file_name)
    if file.exists():
        os.remove(file)
    soft_save_file()


def cache_by_frame(func: t.Callable) -> t.Callable:
    """Decorator that caches output per-frame"""

    def call_func(*args, **kwargs) -> t.Any:
        cached_output = shared.frame_cache.get(func)
        if cached_output is None:
            shared.frame_cache[func] = func(*args, **kwargs)

        return shared.frame_cache.get(func)

    return call_func


def get_icon(tinge="white") -> pygame.Surface:
    icon = pygame.image.load(shared.ASSETS_FOLDER / "images/logo.png")
    surf = pygame.Surface(icon.get_size())
    surf.fill(tinge)

    icon.blit(surf, (0, 0), special_flags=pygame.BLEND_MULT)

    return icon


def _gausian_sub(char: str):
    if char in shared.file_name:
        return shared.file_name[shared.file_name.find(char) + 1 :]

    return shared.file_name


def set_windows_title_bar_color() -> None:
    from ctypes import byref, c_int, sizeof, windll

    info = pygame.display.get_wm_info()
    HWND = info["window"]

    # https://stackoverflow.com/questions/67444141/how-to-change-the-title-bar-in-tkinter
    color = shared.theme["default-bg"][1:]
    r1, r2, g1, g2, b1, b2 = color
    windll_color = f"0x00{b1}{b2}{g1}{g2}{r1}{r2}"
    title_bar_color = int(windll_color, base=16)

    windll.dwmapi.DwmSetWindowAttribute(
        HWND, 35, byref(c_int(title_bar_color)), sizeof(c_int)
    )


def set_windows_title() -> None:
    if platform.system != "Windows":
        return
    title_bar_text = shared.APP_NAME

    if shared.file_name is not None:
        file_name = shared.file_name
        file_name = _gausian_sub("/")
        file_name = _gausian_sub("\\")
        title_bar_text = f"{shared.APP_NAME} - {file_name}"
    w = int(shared.srect.width / 3.5)

    pre_check_title = "⬞" + title_bar_text.rjust(w // 2)
    if len(pre_check_title) < 255:
        title_bar_text = pre_check_title
    else:
        title_bar_text = ""

    pygame.display.set_caption(title_bar_text)


def offset_font_size(offset: int):
    shared.FONT_SIZE += offset
    shared.FONT = pygame.font.Font(shared.FONT_PATH, shared.FONT_SIZE)
    shared.FONT_WIDTH = shared.FONT.render("w", True, "white").get_width()
    shared.FONT_HEIGHT = shared.FONT.get_height()
    shared.chars_changed = True
    if not hasattr(shared, "cursor"):
        return
    shared.cursor.gen_image()


def center_cursor():
    shared.scroll.y = -shared.cursor_pos.y * shared.FONT_HEIGHT
    shared.scroll.y += shared.srect.height / 2
    shared.scroll.y = min(shared.scroll.y, 0)
    shared.chars_changed = True


@cache_by_frame
def is_event_frame(event_type: int) -> bool:
    for event in shared.events:
        if event.type == event_type:
            return True
    return False


@cache_by_frame
def get_text():
    text = ""
    for row in shared.chars:
        text += "".join(row) + "\n"
    return text
