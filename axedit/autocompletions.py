from string import ascii_letters

import jedi
import pygame

from axedit import shared
from axedit.funcs import get_text
from axedit.utils import InputManager

_POSSIBLE_COMPLETIONS = {
    "module": ("󰅩", "purple"),
    "class": ("", "yellow"),
    "param": ("󰭅", "cyan"),
    "function": ("", "seagreen"),
    "statement": ("", "green"),
    "keyword": ("", "magenta"),
    "instance": ("", "aquamarine"),
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
        self.shared_suggestion_length = 0
        self.input_manager = InputManager({pygame.K_RETURN: self.on_completion})

    def on_completion(self):
        if not self.suggestions:
            self.after_autocompletion()
            return
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
            word_index = 0
        top_suggestion = self.suggestions[0].name

        max_index = word_index + len(top_suggestion)
        if max_index > len(line):
            max_index = len(line)
        self.shared_suggestion_length = len(line[word_index:max_index])
        if self.shared_suggestion_length == len(top_suggestion):
            self.after_autocompletion()

    def gen_suggestions(self):
        script = jedi.Script(code=get_text())
        try:
            self.suggestions = script.complete(
                shared.cursor_pos.y + 1, shared.cursor_pos.x
            )
        except ValueError as e:
            print(e)
            # print(f"{shared.cursor_pos.x = }, {shared.cursor_pos.y = }")
            # print(get_text())

        self.calc_shared_suggestion_length()

    def at_autocompletion(self):
        self.pos_at_autocompleting = shared.cursor_pos.x - self.shared_suggestion_length
        shared.autocompleting = True

    def after_autocompletion(self):
        shared.autocompleting = False
        self.suggestions = []

    def is_typing_variable(self):
        for event in shared.events:
            if event.type == pygame.TEXTINPUT:
                if event.text.isalpha() or event.text in "._":
                    return True

        return False

    def is_python_file(self) -> bool:
        return shared.file_name is not None and shared.file_name.endswith(".py")

    def is_typing_breaker(self) -> bool:
        for event in shared.events:
            if event.type == pygame.TEXTINPUT:
                if not event.text.isalpha() and event.text not in "._":
                    return True

        return False

    def is_non_empty_line(self) -> bool:
        return bool("".join(shared.chars[shared.cursor_pos.y]).strip())

    def update(self):
        if (
            self.is_typing_variable()
            and self.is_python_file()
            and self.is_non_empty_line()
        ):
            self.gen_suggestions()
            self.at_autocompletion()

        if self.is_typing_breaker():
            self.after_autocompletion()
            return

        self.input_manager.update(shared.events)

    def get_icon_surf(self, suggestion) -> pygame.Surface:
        icon, color = _POSSIBLE_COMPLETIONS.get(suggestion.type, ("", "green"))
        icon += " "
        icon_surf = shared.FONT.render(icon, True, color)
        return icon_surf

    def render_selected_suggestion(self, suggestion, index):
        surf_1 = shared.FONT.render(
            suggestion.name[: self.shared_suggestion_length], True, "white"
        )
        surf_2 = shared.FONT.render(
            suggestion.name[self.shared_suggestion_length :], True, "grey"
        )
        icon_surf = self.get_icon_surf(suggestion)

        self.image.blit(icon_surf, (0, index * shared.FONT_HEIGHT))
        self.image.blit(surf_1, (icon_surf.get_width(), index * shared.FONT_HEIGHT))
        self.image.blit(
            surf_2,
            (icon_surf.get_width() + surf_1.get_width(), index * shared.FONT_HEIGHT),
        )

    def render_generic_suggestion(self, suggestion, index):
        surf = shared.FONT.render(suggestion.name, True, "grey")
        icon_surf = self.get_icon_surf(suggestion)
        self.image.blit(icon_surf, (0, index * shared.FONT_HEIGHT))
        self.image.blit(surf, (icon_surf.get_width(), index * shared.FONT_HEIGHT))

    def blit_surf_by_relevance(self, suggestion, index) -> pygame.Surface:
        if index == self.selected_suggestion_index:
            self.render_selected_suggestion(suggestion, index)
        else:
            self.render_generic_suggestion(suggestion, index)

    def render_suggestions(self):
        SUGGESTION_BOX_WIDTH = (
            max(len(suggestion.name) for suggestion in self.suggestions) + 2
        ) * shared.FONT_WIDTH
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
