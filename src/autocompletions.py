import jedi
import pygame

from src import shared
from src.funcs import get_text


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
        self.can_autocomplete = False

    def gen_suggestions(self):
        script = jedi.Script(code=get_text())
        self.suggestions = script.complete(shared.cursor_pos.y + 1, shared.cursor_pos.x)
        self.suggestions = [suggestion.name for suggestion in self.suggestions]

    def update(self):
        if (
            shared.file_name is None
            or not shared.file_name.endswith(".py")
            or shared.cursor_pos.x == 0
        ):
            return

        self.gen_suggestions()

    def shared_suggestion_length(self):
        # TODO
        ...

    def render_suggestions(self):
        if not self.suggestions:
            return

        SUGGESTION_BOX_WIDTH = (
            max(len(suggestion) for suggestion in self.suggestions) * shared.FONT_WIDTH
        )
        SUGGESTION_BOX_HEIGHT = len(self.suggestions) * shared.FONT_HEIGHT

        self.image = pygame.Surface((SUGGESTION_BOX_WIDTH, SUGGESTION_BOX_HEIGHT))
        self.image.fill(AutoCompletions.DEFAULT_COLOR)

        selected_background = pygame.Surface((SUGGESTION_BOX_WIDTH, shared.FONT_HEIGHT))
        selected_background.fill(AutoCompletions.SELECTED_COLOR)
        for index, suggestion in enumerate(self.suggestions):
            surf = shared.FONT.render(suggestion, True, "white")

            if self.selected_suggestion_index == index:
                self.image.blit(selected_background, (0, index * shared.FONT_HEIGHT))

            self.image.blit(surf, (0, index * shared.FONT_HEIGHT))

    def draw(self, editor_surf: pygame.Surface):
        self.render_suggestions()
        if not self.suggestions:
            return
        editor_surf.blit(
            self.image,
            (
                shared.cursor_pos.x * shared.FONT_WIDTH,
                (shared.cursor_pos.y + 1) * shared.FONT_HEIGHT,
            ),
        )
