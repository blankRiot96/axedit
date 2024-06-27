import ast
import builtins
import keyword
import typing as t
from typing import Any

import pygame

from axedit import shared
from axedit.funcs import get_text, is_event_frame
from axedit.logs import logger
from axedit.module_checker import is_module

LOGICAL_PUNCTUATION = " .(){}[],:;/\\|+=-*%\"'"

_KEYWORDS = keyword.kwlist[3:]
_SINGLETONS = keyword.kwlist[:3]
_BUILTINS = dir(builtins)

_MODULES = set()
_CLASSES = set()
_PRECEDENCE = []

Color: t.TypeAlias = str


class ImportVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.first = True

    def visit_ImportFrom(self, node: ast.ImportFrom | None):
        if not self.first and not shared.import_line_changed:
            return

        mod_name = node.module
        if node.module is None:
            mod_name = "."

        _MODULES.update(mod_name.split("."))

        imports = []
        for naming_node in node.names:
            imports.append(naming_node.name)
            if naming_node.asname is not None:
                imports.append(naming_node.asname)

        for imp in imports:
            if is_module(mod_name, imp):
                _MODULES.add(imp)
            elif is_pascal(imp):
                _CLASSES.add(imp)

    def visit_Import(self, node: ast.Import):
        if not self.first and not shared.import_line_changed:
            return

        for naming_node in node.names:
            _MODULES.add(naming_node.name)

            if hasattr(naming_node, "asname"):
                _MODULES.add(naming_node.asname)


class ClassVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        _CLASSES.add(node.name)


import_visitor = ImportVisitor()
class_visitor = ClassVisitor()


def apply_precedence(word: str) -> Color:
    word = word.strip()
    final_color = shared.theme["default-fg"]

    for color, subclass in _PRECEDENCE:
        if word in subclass:
            final_color = color

    if word.isdigit():
        final_color = shared.theme["const"]

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


def set_string_status(index: int) -> None:
    global last_string_counter, within_line, concluded_doc_string

    last_string_counter = 0
    within_line = True
    concluded_doc_string = True

    for row in shared.chars[:index]:
        row = "".join(row)
        final_index = len(row) - 1

        if not concluded_doc_string and not (
            row.find("'") != -1 or row.find('"') != -1
        ):
            within_line = False
            # return {range(start_index, final_index + 1): shared.theme["string"]}
            continue

        string_counter = 0

        for current_index, char in enumerate(row):
            if within_line and string_counter > 0:
                string_counter -= 1
                continue

            if char in "\"'":
                within_line = True
                starter = None
                if row.count(char * 3) % 2 != 0:
                    concluded_doc_string = not concluded_doc_string
                    if concluded_doc_string:
                        starter = 0
                    string_pos = final_index
                else:
                    string_pos = row.find(char, current_index + 1)
                incomplete_string = string_pos < 0
                if incomplete_string:
                    string_pos = int(10e6)

                if starter is None:
                    r = range(
                        current_index,
                        string_pos + 1,
                    )
                else:
                    r = range(starter, string_pos + 1)

                string_counter = string_pos - current_index
                continue


def index_colors(row: str) -> dict[t.Generator, Color]:
    global last_string_counter, within_line, concluded_doc_string
    color_ranges = {}

    final_index = len(row) - 1
    acc = ""
    start_index = 0

    if not concluded_doc_string and not ("'" in row or '"' in row):
        within_line = False
        return {range(start_index, final_index + 1): shared.theme["string"]}

    # if concluded_doc_string:
    #     if (single := row.find("'''")) != -1:
    #         end_index = single
    #     elif (double := row.find('"""')) != -1:
    #         end_index = double
    #     return {range(start_index, end_index): shared.theme["string"]}

    string_counter = 0

    for current_index, char in enumerate(row):
        if within_line and string_counter > 0:
            string_counter -= 1
            continue

        if char in "\"'":
            within_line = True
            starter = None
            if row.count(char * 3) % 2 != 0:
                concluded_doc_string = not concluded_doc_string
                if concluded_doc_string:
                    starter = 0
                string_pos = final_index
            else:
                string_pos = row.find(char, current_index + 1)
            incomplete_string = string_pos < 0
            if incomplete_string:
                string_pos = int(10e6)

            if starter is None:
                r = range(
                    current_index,
                    string_pos + 1,
                )
            else:
                r = range(starter, string_pos + 1)
            color_ranges[r] = shared.theme["string"]
            string_counter = string_pos - current_index

            start_index = string_pos + 1
            acc = ""
            continue

        if char == "#":
            color_ranges[range(current_index, len(row))] = shared.theme["comment"]

            todo_index = row[current_index:].find("TODO")
            if todo_index == -1:
                return color_ranges

            todo_index += current_index
            color_ranges[range(todo_index, todo_index + 4)] = shared.theme["dep"]

            return color_ranges

        if char == "@":
            bracket_index = row.find("(")
            end_index = len(row) if bracket_index == -1 else bracket_index
            r = range(current_index, end_index)
            color_ranges[r] = shared.theme["const"]
            return color_ranges

        if char in LOGICAL_PUNCTUATION:
            color = apply_precedence(acc)
            if color == shared.theme["default-fg"] and (
                current_index > 0 and char == "(" and row[current_index - 1] != "("
            ):
                color = shared.theme["func"]
                if is_pascal(acc):
                    color = shared.theme["class"]

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
    image = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT), pygame.SRCALPHA)
    for x, char in enumerate(row):
        color = shared.theme["default-fg"]
        for range, ranged_color in color_ranges.items():
            if x in range:
                color = ranged_color

        try:
            char_surf = shared.FONT.render(char, True, color)
        except pygame.error:
            continue
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
colors = []
should_index_colors = False


def apply_syntax_highlighting() -> pygame.Surface:
    global _PRECEDENCE
    if shared.theme_changed or not _PRECEDENCE:
        _PRECEDENCE = [
            (shared.theme["match"], _BUILTINS),
            (shared.theme["class"], _MODULES),
            (shared.theme["class"], _CLASSES),
            (shared.theme["keyword"], _KEYWORDS),
            (shared.theme["const"], _SINGLETONS),
            (shared.theme["var"], ["self"]),
        ]
    global prev_image
    if (
        not shared.theme_changed
        and (not is_event_frame(pygame.VIDEORESIZE))
        and (not shared.chars_changed)
        and (not shared.scrolling)
        and prev_image is not None
    ):
        return prev_image

    global should_index_colors
    should_index_colors = False
    try:
        parsed_source = ast.parse(get_text())
        # Highlight modules
        temp_mod = _MODULES.copy()
        if shared.import_line_changed:
            _MODULES.clear()
            import_visitor.visit(parsed_source)
            import_visitor.first = False

        # Highlight classes
        temp_class = _CLASSES.copy()
        _CLASSES.clear()
        class_visitor.visit(parsed_source)

        should_index_colors = temp_class != _CLASSES or temp_mod != _MODULES
    except SyntaxError:
        pass

    safety_padding = 2
    n_lines_to_render = int(shared.srect.height / shared.FONT_HEIGHT) + safety_padding
    scroll_offset = int(-shared.scroll.y / shared.FONT_HEIGHT)
    visible_lines = shared.chars[scroll_offset : scroll_offset + n_lines_to_render]
    image = pygame.Surface(shared.srect.size, pygame.SRCALPHA)

    global colors
    if prev_image is None or shared.saved or should_index_colors:
        global last_string_counter, within_line, concluded_doc_string
        last_string_counter = 0
        within_line = True
        concluded_doc_string = True

        # print(f"{prev_image is None=}, {shared.saved=}, {should_index_colors=}")
        colors = [index_colors("".join(row)) for row in shared.chars]

    if shared.chars_changed:
        if len(colors) < len(shared.chars):
            colors.insert(shared.cursor_pos.y, {})
        elif len(colors) > len(shared.chars):
            colors.pop(shared.cursor_pos.y)

        set_string_status(shared.cursor_pos.y)
        try:
            colors[shared.cursor_pos.y] = index_colors(
                "".join(shared.chars[shared.cursor_pos.y])
            )
        except IndexError:
            pass

    for y, row in enumerate(visible_lines):
        row = "".join(row)
        color_ranges = colors[y + scroll_offset]
        row_image = line_wise_stitching(row, color_ranges)
        image.blit(row_image, (0, y * shared.FONT_HEIGHT))

    prev_image = image.copy()
    return image
