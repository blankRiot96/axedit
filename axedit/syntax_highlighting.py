import ast
import builtins
import keyword
import typing as t
from typing import Any

import pygame

from axedit import shared
from axedit.funcs import get_text, is_event_frame
from axedit.module_checker import is_module

LOGICAL_PUNCTUATION = " .(){}[],:;/\\|+=-*%\"'"

_KEYWORDS = keyword.kwlist[3:]
_SINGLETONS = keyword.kwlist[:3]
_BUILTINS = dir(builtins)

_MODULES = []
_CLASSES = []


_PRECENDENCE = {
    "steelblue": _BUILTINS,
    "aquamarine": _MODULES,
    "yellow": _CLASSES,
    "magenta": _KEYWORDS,
    "orange": _SINGLETONS,
    "purple": ["self"],
}

Color: t.TypeAlias = str


class ImportVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        _CLASSES.append(node.name)

    def visit_ImportFrom(self, node: ast.ImportFrom | None):
        mod_name = node.module
        if node.module is None:
            mod_name = "."

        _MODULES.extend(mod_name.split("."))

        imports = []
        for naming_node in node.names:
            imports.append(naming_node.name)
            if naming_node.asname is not None:
                imports.append(naming_node.asname)

        for imp in imports:
            if is_module(mod_name, imp):
                _MODULES.append(imp)
            elif is_pascal(imp):
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
    if word[0] == "_":
        return is_pascal(word[1:])
    return word[0].isupper() and word.find("_") == -1


last_string_counter = 0
within_line = True
concluded_doc_string = True


def index_colors(row: str) -> dict[t.Generator, Color]:
    global last_string_counter, within_line, concluded_doc_string
    color_ranges = {}

    final_index = len(row) - 1
    acc = ""
    start_index = 0

    # if last_string_counter > 0 and not (row.find("'") != -1 or row.find('"') != -1):
    if not concluded_doc_string and not (row.find("'") != -1 or row.find('"') != -1):
        within_line = False
        return {range(start_index, final_index + 1): "green"}

    string_counter = 0

    for current_index, char in enumerate(row):
        if within_line and string_counter > 0:
            string_counter -= 1
            # last_string_counter = string_counter
            continue

        if char in "\"'":
            within_line = True
            if row.count(char * 3) % 2 != 0:
                concluded_doc_string = not concluded_doc_string
                string_pos = final_index
            else:
                string_pos = row.find(char, current_index + 1)
            incomplete_string = string_pos < 0
            if incomplete_string:
                string_pos = int(10e6)

            r = range(
                current_index,
                string_pos + 1,
            )
            color_ranges[r] = "green"
            string_counter = string_pos - current_index
            # last_string_counter = string_counter

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
            if finder:
                remaining = finder + 4
            else:
                remaining = current_index + finder
            color_ranges[range(remaining, final_index + 1)] = comment_color

            return color_ranges

        # if current_index > 0 and char == "(" and row[current_index - 1] != "(":
        #     color = "seagreen"
        #     if is_pascal(acc):
        #         color = "yellow"
        #     color_ranges[range(start_index, current_index)] = color
        #     start_index = current_index + 1
        #     acc = ""
        #     continue

        if char in LOGICAL_PUNCTUATION:
            color = apply_precedence(acc)
            if color == "white" and (current_index > 0 and char == "(" and row[current_index - 1] != "("):
                color = "seagreen"
                if is_pascal(acc):
                    color = "yellow"

                color_ranges[range(start_index, current_index)] = color
                start_index = current_index + 1
                acc = ""
                continue

            color_ranges[range(start_index, current_index)] = color
            start_index = current_index + 1
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
    if not is_event_frame(pygame.VIDEORESIZE) and shared.saved and prev_image is not None and not pygame.event.get(pygame.VIDEORESIZE):
        return prev_image

    _MODULES.clear()
    _CLASSES.clear()

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
