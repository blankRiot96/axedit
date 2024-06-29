"""File that defines some modal commands"""

import re

import clipboard

from axedit import shared
from axedit.classes import CharList, Pos
from axedit.funcs import center_cursor
from axedit.logs import logger
from axedit.state_enums import FileState


def on_percent() -> None:
    brakies = {"(": ")", "[": "]", "{": "}"}
    invert_brakies = {closed: opened for opened, closed in brakies.items()}
    current_char = shared.chars[shared.cursor_pos.y][shared.cursor_pos.x]

    # If sitting on opening bracket
    if current_char in brakies:
        for y_offset, row in enumerate(shared.chars[shared.cursor_pos.y :]):
            row: list
            try:
                start_find = shared.cursor_pos.x + 1 if y_offset == 0 else 0
                # logger.debug(f"{"".join(row)=}, {brakies[current_char]=}, {start_find=}")

                ignore_count = 0
                for i, char in enumerate(row[start_find:]):
                    if char == current_char:
                        ignore_count += 1
                        continue

                    if char == brakies[current_char]:
                        if ignore_count > 0:
                            ignore_count -= 1
                            continue
                        found_x_pos = start_find + i
                        break
                else:
                    raise ValueError
                shared.cursor_pos.y += y_offset
                shared.cursor_pos.x = found_x_pos
                break
            except ValueError:
                continue
        return

    # If sitting on closing bracket
    if current_char in brakies.values():
        for y_offset, row in enumerate(
            reversed(shared.chars[: shared.cursor_pos.y + 1])
        ):
            row: list
            try:
                # start_find = len(row) - shared.cursor_pos.x if y_offset == 0 else -1
                start_find = shared.cursor_pos.x if y_offset == 0 else len(row)

                ignore_count = 0
                # logger.debug(row[:start_find][::-1])
                for i, char in enumerate(row[:start_find][::-1]):
                    if char == current_char:
                        ignore_count += 1
                        continue

                    if char == invert_brakies[current_char]:
                        if ignore_count > 0:
                            ignore_count -= 1
                            continue
                        found_x_pos = start_find - i - 1
                        break
                else:
                    raise ValueError

                shared.cursor_pos.y -= y_offset
                shared.cursor_pos.x = found_x_pos
                break
            except ValueError:
                continue
        return

    # If sitting on non-bracket character
    for y_offset, row in enumerate(reversed(shared.chars[: shared.cursor_pos.y + 1])):
        row: list

        start_find = shared.cursor_pos.x if y_offset == 0 else len(row)

        for i_offset, char in enumerate(reversed(row[:start_find])):
            if char in brakies:
                found_x_pos = start_find - i_offset - 1
                break
        else:
            continue

        shared.cursor_pos.x = found_x_pos
        shared.cursor_pos.y -= y_offset
        break


def on_w(y: int | None = None):
    new_line = y is not None
    if y is None:
        y = shared.cursor_pos.y

    if y >= len(shared.chars):
        return

    if not shared.chars[y]:
        shared.cursor_pos.x = 0
        if new_line:
            return

        shared.cursor_pos.y += 1
        on_w(shared.cursor_pos.y)
        return

    is_word_constituent = lambda char: char.isalnum() or char == "_"
    start_search = new_line
    prev_char: str = shared.chars[y][shared.cursor_pos.x]
    for extra_i, char in enumerate(shared.chars[y][shared.cursor_pos.x :]):
        char: str
        if char.isspace():
            start_search = True
            prev_char = char
            continue

        if is_word_constituent(prev_char):
            if not is_word_constituent(prev_char):
                start_search = True
        else:
            if is_word_constituent(prev_char):
                start_search = True

        if start_search:
            shared.cursor_pos.x += extra_i
            break
    else:
        if shared.cursor_pos.y == len(shared.chars) - 1:
            return
        shared.cursor_pos.x = 0
        shared.cursor_pos.y += 1
        on_w(shared.cursor_pos.y)


# TODO
def on_e(y: int | None = None):
    new_line = y is not None
    if y is None:
        y = shared.cursor_pos.y

    if y >= len(shared.chars):
        return

    if not shared.chars[y]:
        shared.cursor_pos.x = 0
        if new_line:
            return

        shared.cursor_pos.y += 1
        on_e(shared.cursor_pos.y)
        return

    is_word_constituent = lambda char: char.isalnum() or char == "_"
    start_search = new_line
    prev_char: str = shared.chars[y][shared.cursor_pos.x]
    for extra_i, char in enumerate(shared.chars[y][shared.cursor_pos.x :]):
        char: str
        if char.isspace():
            start_search = True
            prev_char = char
            continue

        if is_word_constituent(prev_char):
            if not is_word_constituent(prev_char):
                start_search = True
        else:
            if is_word_constituent(prev_char):
                start_search = True

        if start_search:
            shared.cursor_pos.x += extra_i - 1
            break
    else:
        if shared.cursor_pos.y == len(shared.chars) - 1:
            return
        shared.cursor_pos.x = 0
        shared.cursor_pos.y += 1
        on_e(shared.cursor_pos.y)


def on_y():
    if shared.mode != FileState.VISUAL:
        return


def on_p():
    try:
        paste_output = clipboard.paste()
    except UnicodeDecodeError:
        return
    paste_lines = paste_output.split("\n")

    shared.cursor_pos.x += 1
    saved_pos = Pos(shared.cursor_pos.x, shared.cursor_pos.y)

    store_it = shared.chars[shared.cursor_pos.y][shared.cursor_pos.x :]
    for line in paste_lines:
        given_line = shared.chars[shared.cursor_pos.y]
        shared.chars[shared.cursor_pos.y] = given_line[: shared.cursor_pos.x] + list(
            line
        )

        shared.cursor_pos.y += 1
        shared.chars.insert(shared.cursor_pos.y, CharList([]))
        shared.cursor_pos.x = 0
    shared.chars[shared.cursor_pos.y - 2].extend(store_it)

    # Totally not monkey patching!!
    for _ in range(2):
        shared.chars.pop()

    shared.cursor_pos = Pos(saved_pos.x, saved_pos.y)


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

    if (shared.cursor_pos.y * shared.FONT_HEIGHT) > shared.scroll.y:
        center_cursor()


def on_dollar_sign():
    shared.cursor_pos.x = len(shared.chars[shared.cursor_pos.y]) - 1


def on_zero():
    shared.cursor_pos.x = 0


def on_dd():
    if len(shared.chars) == 1:
        shared.chars[0] = CharList([])
        return
    match = re.match(r".\d.", shared.action_str)
    if match is None:
        match = re.match(r"\d", shared.action_str)
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
    shared.scroll.x, shared.scroll.y = 0, 0
    shared.cursor_pos.x, shared.cursor_pos.y = 0, 0
    shared.chars_changed = True


def on_G():
    shared.cursor_pos.y = len(shared.chars) - 1
    shared.cursor_pos.x = len(shared.chars[-1])
    center_cursor()
