import sys
import typing as t

import tree_sitter
import tree_sitter_rust
from colorama import Fore

p = tree_sitter.Parser(tree_sitter.Language(tree_sitter_rust.language()))

file = "test.rs" if len(sys.argv) == 1 else sys.argv[1]
with open(file, "rb") as f:
    code = f.read()
    tree = p.parse(code)


def traverse_tree(tree: tree_sitter.Tree) -> t.Iterator[tree_sitter.Node]:
    cursor = tree.walk()

    visited_children = False
    while True:
        if not visited_children:
            if not cursor.goto_first_child():
                visited_children = True
                yield cursor.node
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break


# list(traverse_tree(tree))
# print(list(traverse_tree(tree)))
for node in traverse_tree(tree):
    print(node.text.decode(), end=" ")
