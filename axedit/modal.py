"""File that defines some modal commands"""

import re

import clipboard

from axedit import shared
from axedit.classes import CharList
from axedit.funcs import center_cursor
from axedit.logs import logger
from axedit.state_enums import FileState


def on_y():
    if shared.mode != FileState.VISUAL:
        return


def on_p():
    paste_output = clipboard.paste()
    paste_lines = paste_output.split("\n")

    for line in paste_lines:
        given_line = shared.chars[shared.cursor_pos.y]
        logger.debug(f"{given_line=}")
        logger.debug(line)
        shared.chars[shared.cursor_pos.y] = (
            given_line[: shared.cursor_pos.x]
            + list(line)
            + given_line[shared.cursor_pos.x :]
        )
        shared.chars.append(CharList([]))
        shared.cursor_pos.y += 1
        shared.cursor_pos.x = 0


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
    if len(shared.chars) == 1:
        shared.chars[0] = CharList([])
        return
    match = re.match(".\d.", shared.action_str)
    if match is None:
        match = re.match("\d", shared.action_str)
    if match is None:
        n_lines = 1
    else:
        start, end = match.span()
        n_lines = shared.action_str[start:end]
        n_lines = int(n_lines)
    copy_output = ""
    for _ in range(n_lines):
        try:
            copy_output += "".join(shared.chars.pop(shared.cursor_pos.y)) + "\n"
        except IndexError:
            break

    clipboard.copy(copy_output)


def on_d():
    if shared.action_str != "d" or shared.mode != FileState.VISUAL:
        return

    if shared.cursor_pos.x > shared.visual_mode_axis.x:
        shared.cursor_pos.x = shared.visual_mode_axis.x

    shared.chars_changed = True
    shared.mode = FileState.NORMAL
    shared.action_queue.clear()
    shared.action_str = ""


def on_zz():
    center_cursor()


def on_gg():
    shared.cursor_pos.x, shared.cursor_pos.y = 0, 0


def on_G():
    shared.cursor_pos.y = len(shared.chars) - 1
    shared.cursor_pos.x = len(shared.chars[-1])
