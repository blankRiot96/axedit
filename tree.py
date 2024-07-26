import sys
import typing as t
from pathlib import Path

import tree_sitter
from rich.console import Console

file = "test.rs" if len(sys.argv) == 1 else sys.argv[1]

language = Path(file).suffix
language_mapping = {".rs": "rust", ".py": "python"}

language_id = language_mapping.get(language)
module = __import__(f"tree_sitter_{language_id}")

p = tree_sitter.Parser(tree_sitter.Language(module.language()))
with open(file, "rb") as f:
    code = f.read()
    tree = p.parse(code)


node_types: dict[int, str] = {}


def traverse_tree(tree: tree_sitter.Tree) -> t.Iterator[tree_sitter.Node]:
    cursor = tree.walk()

    visited_children = False
    prev_nodes = []
    while True:
        if not visited_children:
            if not cursor.goto_first_child():
                if cursor.node.type == "identifier":
                    node_types[cursor.node.start_byte] = prev_nodes[-2].type + "-id"
                yield cursor.node
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break

        prev_nodes.append(cursor.node)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def print_color(hex_color):
    rgb = hex_to_rgb(hex_color)
    print(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m", end="")


default_bg = "#1e1e2e"
light_bg = "#181825"
select_bg = "#313244"
comment = "#45475a"
dark_fg = "#585b70"
default_fg = "#cdd6f4"
light_fg = "#f5e0dc"
light_bg = "#b4befe"
var = "#f38ba8"
int_const_bool = "#fab387"
classes = "#f9e2af"
strings = "#a6e3a1"
match = "#94e2d5"
func = "#89b4fa"
keywords = "#cba6f7"
deprecated = "#f2cdcd"

SCHEMA = {
    keywords: (
        "fn",
        "def",
        "if",
        "match",
        "import",
        "while",
        "not",
        "pass",
        "return",
        "for",
        "elif",
        "else",
        "class",
    ),
    strings: ("string_content", '"', "string_start", "string_end"),
    int_const_bool: ("integer_literal", "integer", "false", "true"),
    classes: ("class-id", "dotted_name-id", "attribute-id"),
    comment: ("comment",),
    func: ("def-id",),
    var: ("typed_parameter-id", "type-id"),
}
COLORS = {}
for color, types in SCHEMA.items():
    for ty in types:
        COLORS[ty] = color

if "--nodes" in sys.argv:
    print(*{node.type for node in traverse_tree(tree)}, sep="\n")
    exit()
elif "--tree" in sys.argv:
    print(tree.root_node)
    exit()
elif "--id" in sys.argv:
    list(traverse_tree(tree))
    print(*node_types.values(), sep="\n")
    exit()

console = Console()
nodes = traverse_tree(tree)
next_node = next(nodes)
for current_byte, char in enumerate(code.decode()):
    if current_byte == next_node.start_byte:
        node_type = next_node.type
        if next_node.type == "identifier":
            node_type = node_types.get(current_byte)
            # print(f"<{node_type}>:", end="")
        color = COLORS.get(node_type, "#ffffff")
        print_color(color)
        try:
            next_node = next(nodes)
        except StopIteration:
            pass
    print(char, end="")
