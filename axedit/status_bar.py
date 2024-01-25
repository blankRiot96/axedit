import pygame

from axedit import shared
from axedit.utils import render_at


class StatusBar:
    """
    file_name -> None
    loc -> shared.cursor_pos
    mode -> shared.mode
    """

    def __init__(self) -> None:
        self.status_str = "FILE: {file_name}{saved} | MODE: {mode} | LOC: {loc}"
        self.gen_surf()

    def get_saved_status(self) -> str:
        if shared.file_name is None:
            return ""

        if shared.saved:
            return ""

        return "*"

    def get_file_name(self) -> str | None:
        if shared.file_name is None:
            return

        return self.get_saved_status() + shared.file_name.replace("\\", "/")

    def add_loc(self, n_chars: int, out_str: str):
        loc_str = f"{shared.cursor_pos.x + 1},{shared.cursor_pos.y + 1}"
        out_str += " " * (n_chars - len(out_str) - len(loc_str) - 1)
        out_str += loc_str

        return out_str

    def add_file_name(self, out_str: str) -> str:
        file_name = self.get_file_name()
        if file_name is None:
            return out_str

        out_str += " "
        file_name = f" {file_name} "
        angle_offset = 20
        poly_botleft = shared.FONT_WIDTH * len(out_str), shared.FONT_HEIGHT
        poly_topleft = poly_botleft[0] + angle_offset, 0
        poly_topright = (
            poly_topleft[0] + (len(file_name) * shared.FONT_WIDTH),
            0,
        )
        poly_botright = poly_topright[0] - angle_offset, shared.FONT_HEIGHT

        points = [poly_botleft, poly_topleft, poly_topright, poly_botright]
        pygame.draw.polygon(self.surf, (24, 12, 21), points)
        out_str += f"{file_name}"

        return out_str

    def action_queue_to_str(self) -> str:
        final = ""
        for action in shared.action_queue:
            if action == "ctrl":
                final += "^"
            else:
                final += action

        return final

    def add_action_queue(self, n_chars: int, out_str: str) -> str:
        action_str = self.action_queue_to_str()
        out_str += " " * (n_chars - len(out_str) - len(action_str) - 1)
        out_str += action_str

        return out_str

    def gen_surf(self):
        # out_str = self.status_str.format(
        #     saved=self.get_saved_status(),
        #     file_name=self.get_file_name(),
        #     mode=shared.mode.name,
        #     loc=f"{shared.cursor_pos.x}, {shared.cursor_pos.y}",
        # )
        self.surf = pygame.Surface((shared.srect.width, shared.FONT_HEIGHT))
        self.surf.fill((48, 25, 52))

        n_chars = int(shared.srect.width / shared.FONT_WIDTH)
        out_str = f"--{shared.mode.name}--"
        out_str = self.add_file_name(out_str)
        # out_str = self.add_loc(n_chars, out_str)
        out_str = self.add_action_queue(n_chars, out_str)
        render_at(
            self.surf, shared.FONT.render(out_str, True, "white"), "midleft", (5, 0)
        )

    def update(self):
        ...

    def draw(self):
        self.gen_surf()
