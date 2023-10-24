import itertools
import keyword
import typing as t
from string import punctuation

import pygame

from src import shared

WORDS = []

_KEYWORDS = keyword.kwlist[3:]
_SINGLETONS = keyword.kwlist[:3]
_BUILTINS = dir(__builtins__)

_PRECENDENCE = {
    "magenta": _KEYWORDS,
    "orange": _SINGLETONS,
    "cyan": _BUILTINS,
}


current_pos = 0

Color: t.TypeAlias = str


def peek():
    return WORDS[current_pos + 1]


def prev():
    try:
        return WORDS[current_pos - 1]
    except IndexError:
        return None


def is_module(color: str) -> Color:
    if prev() == "import":
        return "seagreen"

    return color


def apply_precedence(word: str) -> Color:
    word = word.strip()
    final_color = "white"
    for color, subclass in _PRECENDENCE.items():
        if word in subclass:
            final_color = color

    final_color = is_module(final_color)

    return final_color


def remove_punctuation(word: str):
    out = "".join(char for char in word if char not in punctuation)
    return out


def stitch_image(color_index: dict[str, Color]) -> pygame.Surface:
    image = pygame.Surface(shared.srect.size, pygame.SRCALPHA)
    words = ["".join(row).split() for row in shared.chars]
    chars_consumed = 0
    for y, row in enumerate(words):
        for x, word in enumerate(row):
            color = color_index.get(word, "white")
            word_surf = shared.FONT.render(word, True, color)
            image.blit(
                word_surf,
                ((chars_consumed + x) * shared.FONT_WIDTH, y * shared.FONT_HEIGHT),
            )

            chars_consumed += len(word)
        chars_consumed = 0

    return image


def alternative_stitch(color_index: dict[str, Color]) -> pygame.Surface:
    image = pygame.Surface(shared.srect.size, pygame.SRCALPHA)
    word_consumed = ""
    for y, row in enumerate(shared.chars):
        for x, col in enumerate(row):
            color = color_index.get(word_consumed, "white")

            word_consumed += col
            if col == " ":
                word_surf = shared.FONT.render(word_consumed.strip(), True, color)
                image.blit(
                    word_surf,
                    (x * shared.FONT_WIDTH, y * shared.FONT_HEIGHT),
                )
                word_consumed = ""

    return image


def index_colors() -> dict[str, Color]:
    global current_pos

    color_index = {}
    for word in WORDS:
        color = apply_precedence(word)
        color_index[word] = color
        current_pos += 1

    return color_index


def generate_words():
    global WORDS
    char_copy = shared.chars.copy()
    for row in char_copy:
        row.append("\n")
    WORDS = itertools.chain(*char_copy)
    WORDS = filter(lambda char: char not in punctuation, WORDS)
    WORDS = "".join(WORDS).split()


def index_colors_2(row: list[str]) -> dict[t.Generator, Color]:
    color_ranges = {}

    acc = ""
    start_index = 0
    for current_index, char in enumerate(row):
        if char in " " + punctuation:
            color = apply_precedence(acc)
            color_ranges[range(start_index, current_index)] = color
            start_index = current_index
            acc = ""
            continue
        acc += char

    return color_ranges


# def apply_syntax_highlighting() -> pygame.Surface:
# global current_pos
# current_pos = 0
# generate_words()
# color_index = index_colors()
# image = stitch_image(color_index)
# return image


def line_wise_stitching(row: list[str], color_ranges: dict) -> pygame.Surface:
    image = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT))
    for x, char in enumerate(row):
        color = "white"
        for range, ranged_color in color_ranges.items():
            if x in range:
                color = ranged_color

        char_surf = shared.FONT.render(char, True, color)
        image.blit(char_surf, (x * shared.FONT_WIDTH, 0))

    return image


def apply_syntax_highlighting() -> pygame.Surface:
    image = pygame.Surface(shared.srect.size, pygame.SRCALPHA)
    for y, row in enumerate(shared.chars):
        color_ranges = index_colors_2(row)
        row_image = line_wise_stitching(row, color_ranges)

        image.blit(row_image, (0, y * shared.FONT_HEIGHT))

    return image
