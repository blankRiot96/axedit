import jedi
import pygame

from axedit import shared
from axedit.funcs import get_text
from axedit.input_queue import InputManager
from axedit.logs import logger
from axedit.state_enums import FileState

_POSSIBLE_COMPLETIONS = {}


class AutoCompletions:
    """
    Serves autocompletions using jedi
    Renders them as a box
    """

    SELECTED_COLOR = (100, 100, 100)
    DEFAULT_COLOR = (50, 50, 50)
    MAX_SUGGESTIONS = 10

    def __init__(self) -> None:
        self.image: pygame.Surface | None = None
        self.suggestions = []
        self.selected_suggestion_index = 0
        self.pos_at_autocompleting = 0
        self.shared_suggestion_length = 0
        self.input_manager = InputManager(
            {
                pygame.K_RETURN: self.on_completion,
                pygame.K_TAB: self.on_completion,
                pygame.K_UP: self.cycle_suggestions_up,
                pygame.K_DOWN: self.cycle_suggestions_down,
            }
        )

        self.suggestion_offset = 0

    def offset_cycle(self):
        suggestion_diff = self.selected_suggestion_index - (
            AutoCompletions.MAX_SUGGESTIONS / 2
        )
        if suggestion_diff > 0:
            self.suggestion_offset = int(suggestion_diff)
            return

        self.suggestion_offset = 0

    def cycle_suggestions_up(self):
        if not shared.autocompleting:
            return
        self.selected_suggestion_index -= 1

        if self.selected_suggestion_index < 0:
            self.selected_suggestion_index = len(self.suggestions) - 1

        self.offset_cycle()

    def cycle_suggestions_down(self):
        if not shared.autocompleting:
            return
        self.selected_suggestion_index += 1

        if self.selected_suggestion_index > len(self.suggestions) - 1:
            self.selected_suggestion_index = 0

        self.offset_cycle()

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
            logger.warn(e)
           
            # print(f"{shared.cursor_pos.x = }, {shared.cursor_pos.y = }")
            # print(get_text())

        self.calc_shared_suggestion_length()

    def at_autocompletion(self):
        self.pos_at_autocompleting = shared.cursor_pos.x - self.shared_suggestion_length
        shared.autocompleting = bool(self.suggestions)

    def after_autocompletion(self):
        self.suggestion_offset = 0
        shared.autocompleting = False
        self.suggestions = []

    def is_typing_variable(self):
        if shared.mode in (FileState.NORMAL, FileState.VISUAL):
            return

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

    def on_theme_change(self):
        global _POSSIBLE_COMPLETIONS

        if not _POSSIBLE_COMPLETIONS or shared.theme_changed:
            _POSSIBLE_COMPLETIONS = {
                "module": ("󰅩", shared.theme["class"]),
                "class": ("", shared.theme["class"]),
                "param": ("󰭅", shared.theme["var"]),
                "function": ("", shared.theme["func"]),
                "statement": ("", shared.theme["string"]),
                "keyword": ("", shared.theme["keyword"]),
                "instance": ("", shared.theme["const"]),
            }

    def update(self):
        self.on_theme_change()
        if (
            self.is_typing_variable()
            and self.is_python_file()
            and self.is_non_empty_line()
        ):
            self.gen_suggestions()
            self.at_autocompletion()

        if self.is_typing_breaker() or shared.mode == FileState.NORMAL:
            self.after_autocompletion()
            return

        self.input_manager.update()

    def get_icon_surf(self, suggestion) -> pygame.Surface:
        icon, color = _POSSIBLE_COMPLETIONS.get(
            suggestion.type, ("", shared.theme["default-fg"])
        )
        icon += " "
        icon_surf = shared.FONT.render(icon, True, color)
        return icon_surf

    def render_selected_suggestion(self, suggestion, index):
        surf_1 = shared.FONT.render(
            suggestion.name[: self.shared_suggestion_length],
            True,
            shared.theme["keyword"],
        )
        surf_2 = shared.FONT.render(
            suggestion.name[self.shared_suggestion_length :],
            True,
            shared.theme["default-fg"],
        )
        icon_surf = self.get_icon_surf(suggestion)

        self.image.blit(icon_surf, (0, index * shared.FONT_HEIGHT))
        self.image.blit(surf_1, (icon_surf.get_width(), index * shared.FONT_HEIGHT))
        self.image.blit(
            surf_2,
            (icon_surf.get_width() + surf_1.get_width(), index * shared.FONT_HEIGHT),
        )

    def render_generic_suggestion(self, suggestion, index):
        surf = shared.FONT.render(suggestion.name, True, shared.theme["default-fg"])
        icon_surf = self.get_icon_surf(suggestion)
        self.image.blit(icon_surf, (0, index * shared.FONT_HEIGHT))
        self.image.blit(surf, (icon_surf.get_width(), index * shared.FONT_HEIGHT))

    def blit_surf_by_relevance(self, suggestion, index) -> pygame.Surface:
        if index == self.selected_suggestion_index:
            self.render_selected_suggestion(suggestion, index)
        else:
            self.render_generic_suggestion(suggestion, index)

    def render_suggestions(self):
        suggestions_to_be_rendered = self.suggestions[
            self.suggestion_offset : AutoCompletions.MAX_SUGGESTIONS
            + self.suggestion_offset
        ]

        SUGGESTION_BOX_WIDTH = (
            max(len(suggestion.name) for suggestion in suggestions_to_be_rendered) + 2
        ) * shared.FONT_WIDTH
        SUGGESTION_BOX_HEIGHT = len(suggestions_to_be_rendered) * shared.FONT_HEIGHT

        self.image = pygame.Surface((SUGGESTION_BOX_WIDTH, SUGGESTION_BOX_HEIGHT))
        self.image.fill(shared.theme["light-bg"])

        selected_background = pygame.Surface((SUGGESTION_BOX_WIDTH, shared.FONT_HEIGHT))
        selected_background.fill(shared.theme["comment"])

        for index, suggestion in enumerate(suggestions_to_be_rendered):
            index += self.suggestion_offset
            if self.selected_suggestion_index == index:
                self.image.blit(
                    selected_background,
                    (0, (index - self.suggestion_offset) * shared.FONT_HEIGHT),
                )

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
