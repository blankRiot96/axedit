import builtins
import keyword
import typing as t

import pygame

from src import shared

LOGICAL_PUNCTUATION = " .(){}[],:;/\\|+=-*%\"'"

_KEYWORDS = keyword.kwlist[3:]
_SINGLETONS = keyword.kwlist[:3]
_BUILTINS = dir(builtins)
_BUILTINS.extend(["self"])
_MODULES = []
_METHODS = []
_CLASSES = []

_PRECENDENCE = {
    "cyan": _BUILTINS,
    "aquamarine": _MODULES,
    "seagreen": _METHODS,
    "yellow": _CLASSES,
    "magenta": _KEYWORDS,
    "orange": _SINGLETONS,
}

Color: t.TypeAlias = str


def add_context(word: str, prev_word: str) -> Color:
    if prev_word == "import":
        _MODULES.append(word.strip())
    elif prev_word == "def":
        _METHODS.append(word)
    elif prev_word == "class":
        _CLASSES.append(word)


def apply_precedence(word: str) -> Color:
    word = word.strip()
    final_color = "white"
    for color, subclass in _PRECENDENCE.items():
        if word in subclass:
            final_color = color

    if word.isdigit():
        final_color = "tomato"

    return final_color


def index_colors(row: str) -> dict[t.Generator, Color]:
    color_ranges = {}

    final_index = len(row) - 1
    acc = ""
    start_index = 0
    prev_word = ""

    string_counter = 0

    for current_index, char in enumerate(row):
        if string_counter > 0:
            string_counter -= 1
            continue

        if char in "\"'":
            string_pos = row.find(char, current_index + 1)
            if string_pos < 0:
                string_pos = int(10e6)
            r = range(
                current_index,
                string_pos + 1,
            )
            color_ranges[r] = "green"
            string_counter = string_pos - current_index

            start_index = string_pos + 1
            acc = ""
            continue

        if char in LOGICAL_PUNCTUATION:
            add_context(acc, prev_word)
            color = apply_precedence(acc)
            color_ranges[range(start_index, current_index)] = color
            start_index = current_index + 1
            prev_word = acc
            acc = ""
            continue
        acc += char

        if current_index == final_index:
            add_context(acc, prev_word)
            color = apply_precedence(acc)
            color_ranges[range(start_index, current_index + 1)] = color

    return color_ranges


def line_wise_stitching(row: str, color_ranges: dict) -> pygame.Surface:
    image = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT))
    for x, char in enumerate(row):
        color = "white"
        for range, ranged_color in color_ranges.items():
            if x in range:
                color = ranged_color

        char_surf = shared.FONT.render(char, True, color)
        image.blit(char_surf, (x * shared.FONT_WIDTH, 0))

    return image


def is_necessary_to_render(y: int, line: str) -> bool:
    if y == shared.cursor_pos.y:
        return True
    stripped = line.strip()
    required_rerenders = ("def", "class", "import")
    for render in required_rerenders:
        if stripped.startswith(render):
            return True

    return False


def apply_syntax_highlighting(
    pre_rendered_lines: dict[str, pygame.Surface]
) -> pygame.Surface:
    _MODULES.clear()
    _CLASSES.clear()
    _METHODS.clear()

    # TODO: Test this
    image = pygame.Surface(
        (shared.srect.width, len(shared.chars) * shared.FONT_HEIGHT), pygame.SRCALPHA
    )
    for y, item in enumerate(zip(shared.chars, pre_rendered_lines)):
        row, surf = item
        row = "".join(row)
        if not is_necessary_to_render(y, row) and surf is not None:
            image.blit(surf, (0, y * shared.FONT_HEIGHT))
            continue
        color_ranges = index_colors(row)
        row_image = line_wise_stitching(row, color_ranges)
        pre_rendered_lines[y] = row_image
        image.blit(row_image, (0, y * shared.FONT_HEIGHT))

    return image
