import ast
import builtins
import keyword
import typing as t

import pygame

from axedit import shared
from axedit.funcs import get_text

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


class ImportVisitor(ast.NodeVisitor):
    def visit_ImportFrom(self, node: ast.ImportFrom):
        _MODULES.extend(node.module.split("."))

        imports = []
        for naming_node in node.names:
            imports.append(naming_node.name)
            if naming_node.asname is not None:
                imports.append(naming_node.asname)

        for imp in imports:
            if is_pascal(imp):
                _CLASSES.append(imp)

    def visit_Import(self, node: ast.Import):
        for naming_node in node.names:
            _MODULES.append(naming_node.name)

            if hasattr(naming_node, "asname"):
                _MODULES.append(naming_node.asname)


import_visitor = ImportVisitor()


def apply_precedence(word: str) -> Color:
    word = word.strip()
    final_color = "white"

    for color, subclass in _PRECENDENCE.items():
        if word in subclass:
            final_color = color

    if word.isdigit():
        final_color = "tomato"

    return final_color


def is_pascal(word: str) -> bool:
    if not word:
        return False
    return word[0].isupper() and word.find("_") == -1


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

        if char == "#":
            finder = 0
            if "TODO" in row[current_index:]:
                finder = row.find("TODO")

            comment_color = (100, 100, 100)
            color_ranges[range(current_index, finder + 1)] = comment_color
            color_ranges[range(finder, finder + 5)] = "red"
            color_ranges[range(finder + 4, final_index + 1)] = comment_color

            return color_ranges

        if current_index > 0 and char == "(" and row[current_index - 1] != "(":
            color = "seagreen"
            if is_pascal(acc):
                color = "yellow"
            color_ranges[range(start_index, current_index)] = color
            start_index = current_index + 1
            prev_word = acc
            acc = ""
            continue

        if char in LOGICAL_PUNCTUATION:
            color = apply_precedence(acc)
            color_ranges[range(start_index, current_index)] = color
            start_index = current_index + 1
            prev_word = acc
            acc = ""
            continue
        acc += char

        if current_index == final_index:
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


prev_image = None


def apply_syntax_highlighting(
    pre_rendered_lines: dict[str, pygame.Surface]
) -> pygame.Surface:
    global prev_image
    if shared.saved and prev_image is not None:
        return prev_image

    _MODULES.clear()
    _CLASSES.clear()
    _METHODS.clear()

    try:
        import_visitor.visit(ast.parse(get_text()))
    except SyntaxError:
        pass

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

    prev_image = image.copy()
    return image
