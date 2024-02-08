"""File that defines some modal commands"""

import re

from axedit import shared
from axedit.funcs import center_cursor
from axedit.state_enums import FileState


def on_dollar_sign():
    shared.cursor_pos.x = len(shared.chars[shared.cursor_pos.y]) - 1


def on_zero():
    shared.cursor_pos.x = 0


def on_dd():
    match = re.match(".\d.", shared.action_str)
    if match is None:
        match = re.match("\d", shared.action_str)
    if match is None:
        n_lines = 1
    else:
        start, end = match.span()
        n_lines = shared.action_str[start:end]
        n_lines = int(n_lines)
    for _ in range(n_lines):
        shared.chars.pop(shared.cursor_pos.y)


def on_d():
    if shared.mode != FileState.VISUAL:
        return

    shared.mode = FileState.NORMAL


def on_zz():
    center_cursor()


def on_gg():
    shared.cursor_pos.x, shared.cursor_pos.y = 0, 0


def on_G():
    shared.cursor_pos.y = len(shared.chars) - 1
    shared.cursor_pos.x = len(shared.chars[-1])
