"""File that defines some modal commands"""

import re

from axedit import shared
from axedit.funcs import center_cursor
from axedit.state_enums import FileState


def on_left_brace():
    good_line_encountered = False
    for i, line in enumerate(shared.chars[: shared.cursor_pos.y + 1][::-1]):
        if line:
            good_line_encountered = True
        elif good_line_encountered:
            shared.cursor_pos.y -= i
            break
    else:
        shared.cursor_pos.y = 0
        shared.cursor_pos.x = 0

    if (shared.cursor_pos.y * shared.FONT_HEIGHT) + shared.scroll.y < 0:
        center_cursor()


def on_right_brace():
    good_line_encountered = False
    for i, line in enumerate(shared.chars[shared.cursor_pos.y :]):
        if line:
            good_line_encountered = True
        elif good_line_encountered:
            shared.cursor_pos.y += i
            break
    else:
        shared.cursor_pos.y = len(shared.chars) - 1
        shared.cursor_pos.x = len(shared.chars[shared.cursor_pos.y]) - 1

    if (
        shared.cursor_pos.y * shared.FONT_HEIGHT
    ) + shared.scroll.y > shared.srect.height:
        center_cursor()


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
    if shared.action_str != "d" or shared.mode != FileState.VISUAL:
        return

    shared.chars_changed = True
    shared.mode = FileState.NORMAL
    shared.action_queue.clear()


def on_zz():
    center_cursor()


def on_gg():
    shared.cursor_pos.x, shared.cursor_pos.y = 0, 0


def on_G():
    shared.cursor_pos.y = len(shared.chars) - 1
    shared.cursor_pos.x = len(shared.chars[-1])
