from string import ascii_letters

import jedi
import pygame

from src import shared
from src.funcs import get_text
from src.utils import InputManager

_POSSIBLE_COMPLETIONS = {
    "module": "blue",
    "class": "yellow",
    "param": "cyan",
    "function": "seagreen",
    "statement": "green",
}


class AutoCompletions:
    """
    Serves autocompletions using jedi
    Renders them as a box
    """

    SELECTED_COLOR = (100, 100, 100)
    DEFAULT_COLOR = (50, 50, 50)

    def __init__(self) -> None:
        self.image: pygame.Surface | None = None
        self.suggestions = []
        self.selected_suggestion_index = 0
        self.pos_at_autocompleting = 0
        self.once = True
        self.shared_suggestion_length = 0
        self.input_manager = InputManager({pygame.K_RETURN: self.on_completion})

    def on_completion(self):
        line = shared.chars[shared.cursor_pos.y]
        shared.chars[shared.cursor_pos.y] = line[: self.pos_at_autocompleting] + list(
            self.suggestions[self.selected_suggestion_index].name
        )
        shared.cursor_pos.x = self.pos_at_autocompleting + len(
            self.suggestions[self.selected_suggestion_index].name
        )
        self.after_autocompletion()

    def calc_shared_suggestion_length(self):
        if not self.suggestions:
            self.after_autocompletion()
            return
        line = "".join(shared.chars[shared.cursor_pos.y])
        nums = [line.rfind("."), line.rfind(" ")]
        nums = [num for num in nums if num > -1]

        if nums:
            word_index = min(nums) + 1
        else:
            word_index = 1
        top_suggestion = self.suggestions[0].name

        max_index = word_index + len(top_suggestion)
        if max_index > len(line):
            max_index = len(line)
        self.shared_suggestion_length = len(line[word_index:max_index])
        if self.shared_suggestion_length == len(top_suggestion):
            self.after_autocompletion()

    def gen_suggestions(self):
        script = jedi.Script(code=get_text())
        self.suggestions = script.complete(shared.cursor_pos.y + 1, shared.cursor_pos.x)
        self.calc_shared_suggestion_length()

    def at_autocompletion(self):
        self.pos_at_autocompleting = shared.cursor_pos.x - self.shared_suggestion_length
        shared.autocompleting = True
        self.once = False

    def after_autocompletion(self):
        shared.autocompleting = False
        self.once = True

    def update(self):
        # TODO: Fix autocomplete conditions
        if (
            shared.file_name is None
            or not shared.file_name.endswith(".py")
            or shared.cursor_pos.x == 0
            or shared.chars[shared.cursor_pos.y][shared.cursor_pos.x - 1]
            not in ascii_letters + "."
            and not shared.autocompleting
            and not shared.text_writing
        ):
            self.suggestions = []
            return

        self.gen_suggestions()
        if self.once:
            self.at_autocompletion()
        self.input_manager.update(shared.events)

    def blit_surf_by_relevance(self, suggestion, index) -> pygame.Surface:
        if index == self.selected_suggestion_index:
            surf_1 = shared.FONT.render(
                suggestion.name[: self.shared_suggestion_length], True, "white"
            )
            surf_2 = shared.FONT.render(
                suggestion.name[self.shared_suggestion_length :], True, "grey"
            )

            self.image.blit(surf_1, (0, index * shared.FONT_HEIGHT))
            self.image.blit(surf_2, (surf_1.get_width(), index * shared.FONT_HEIGHT))
        else:
            surf = shared.FONT.render(suggestion.name, True, "grey")
            self.image.blit(surf, (0, index * shared.FONT_HEIGHT))

    def render_suggestions(self):
        SUGGESTION_BOX_WIDTH = (
            max(len(suggestion.name) for suggestion in self.suggestions)
            * shared.FONT_WIDTH
        )
        SUGGESTION_BOX_HEIGHT = len(self.suggestions) * shared.FONT_HEIGHT

        self.image = pygame.Surface((SUGGESTION_BOX_WIDTH, SUGGESTION_BOX_HEIGHT))
        self.image.fill(AutoCompletions.DEFAULT_COLOR)

        selected_background = pygame.Surface((SUGGESTION_BOX_WIDTH, shared.FONT_HEIGHT))
        selected_background.fill(AutoCompletions.SELECTED_COLOR)
        for index, suggestion in enumerate(self.suggestions):
            if self.selected_suggestion_index == index:
                self.image.blit(selected_background, (0, index * shared.FONT_HEIGHT))

            self.blit_surf_by_relevance(suggestion, index)

    def draw(self, editor_surf: pygame.Surface):
        if not self.suggestions:
            return
        self.render_suggestions()
        editor_surf.blit(
            self.image,
            (
                self.pos_at_autocompleting * shared.FONT_WIDTH,
                (shared.cursor_pos.y + 1) * shared.FONT_HEIGHT,
            ),
        )
