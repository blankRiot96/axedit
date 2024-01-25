import itertools
import math
import time
import typing as t
from functools import lru_cache

import pygame


class Empty:
    def update(self):
        ...

    def draw(self):
        ...


empty = Empty()


class Projectile:
    def __init__(self, radians: float, speed: float) -> None:
        self.radians = radians
        self.speed = speed

    def get_delta_velocity(self, dt: float):
        self.dx = math.cos(self.radians) * self.speed * dt
        self.dy = math.sin(self.radians) * self.speed * dt

        self.dv = pygame.Vector2(self.dx, self.dy)


class SinWave:
    def __init__(self, speed: float) -> None:
        self.rad = 0.0
        self.speed = speed

    def val(self) -> float:
        self.rad += self.speed
        if self.rad >= 2 * math.pi:
            self.rad = 0

        return math.sin(self.rad)


class Time:
    """
    Class to check if time has passed.
    """

    def __init__(self, time_to_pass: float):
        self.time_to_pass = time_to_pass
        self.start = time.perf_counter()

    def reset(self):
        self.start = time.perf_counter()

    def tick(self) -> bool:
        if time.perf_counter() - self.start > self.time_to_pass:
            self.start = time.perf_counter()
            return True
        return False


class TimeOnce:
    """
    Class to check if time has passed.
    """

    def __init__(self, time_to_pass: float):
        self.time_to_pass = time_to_pass
        self.start = time.perf_counter()

    def reset(self):
        self.start = time.perf_counter()

    def tick(self) -> bool:
        if time.perf_counter() - self.start > self.time_to_pass:
            return True
        return False


class Animation:
    def __init__(
        self, frames: t.Sequence[pygame.Surface], time_between_frames: float
    ) -> None:
        self.frames = itertools.cycle(frames)
        self.timer = Time(time_between_frames)
        self.current_frame = next(self.frames)

    def get_next_frame(self):
        self.current_frame = next(self.frames)

    def update(self):
        if self.timer.tick():
            self.get_next_frame()


class ReversiveAnimation:
    def __init__(
        self, frames: t.Sequence[pygame.Surface], time_between_frames: float
    ) -> None:
        self.frames = frames
        self.max_frames = len(self.frames)
        self.__index = 0
        self.timer = Time(time_between_frames)
        self.current_frame: pygame.Surface = self.frames[self.__index]
        self.fact = 1

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, val: int) -> None:
        self.__index = val
        self.current_frame = self.frames[self.__index]

    def get_next_frame(self):
        self.index += self.fact
        if 0 >= self.index or self.max_frames - 1 <= self.index:
            self.fact *= -1

    def update(self):
        if self.timer.tick():
            self.get_next_frame()


class PlayItOnceAnimation(Animation):
    def __init__(
        self,
        frames: t.Sequence[pygame.Surface],
        time_between_frames: float,
        pos: t.Sequence,
    ) -> None:
        self.n_frames = len(frames)
        self.pos = pos
        super().__init__(frames, time_between_frames)
        self.index = 0
        self.done = False

    def get_next_frame(self):
        if self.done:
            return
        super().get_next_frame()
        self.index += 1
        if self.index == self.n_frames - 1:
            self.done = True


@lru_cache
def get_font(file_name: str | None, size: t.Sequence) -> pygame.font.Font:
    return pygame.font.Font(file_name, size)


def circle_surf(radius: float, color) -> pygame.Surface:
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius, radius), radius)
    return surf


def highlight_text(
    font: pygame.font.Font,
    text: str,
    antialias: bool,
    color: str,
    indeces: list[int],
    highlight_color: str,
) -> pygame.Surface:
    size = font.render(text, antialias, "white").get_size()
    surf = pygame.Surface(size, pygame.SRCALPHA)

    acc_width = 0
    for index, char in enumerate(text):
        if index in indeces:
            col = highlight_color
        else:
            col = color

        char_surf = font.render(char, True, col)
        surf.blit(char_surf, (acc_width, 0))
        acc_width += char_surf.get_width()

    return surf


def get_images(
    sheet: pygame.Surface,
    size: tuple[int],
    bound=False,
):
    """
    Converts a sprite sheet to a list of surfaces
    Parameters:
        sheet: A pygame.Surface that contains the sprite sheet
        rows: Amount of rows in the sprite sheet
        columns: Amount of columds in the sprite sheet
        size: Size of a sprite in the sprite sheet
    """
    images = []

    width, height = size

    # loop through all sprites in the sprite sheet
    rows = int(sheet.get_height() / height)
    columns = int(sheet.get_width() / width)

    for row in range(rows):
        for col in range(columns):
            image = sheet.subsurface(pygame.Rect((col * width), (row * height), *size))

            if bound:
                r = image.get_bounding_rect()
                image = image.subsurface(r)

            images.append(image)

    return images


def render_at(
    base_surf: pygame.Surface,
    surf: pygame.Surface,
    pos: str,
    offset: t.Sequence = (0, 0),
) -> None:
    """Renders a surface to a base surface by matching a point.

    Example: render_at(screen, widget, "center")
    """
    base_rect = base_surf.get_rect()
    surf_rect = surf.get_rect()
    setattr(surf_rect, pos, getattr(base_rect, pos))
    surf_rect.x += offset[0]
    surf_rect.y += offset[1]
    base_surf.blit(surf, surf_rect)


def load_scale_3(file_path: str) -> pygame.Surface:
    img = pygame.image.load(file_path).convert_alpha()
    return pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))


def scale_by(img: pygame.Surface, factor: float | int) -> pygame.Surface:
    return pygame.transform.scale(
        img, (img.get_width() * factor, img.get_height() * factor)
    )


def scale_add(img: pygame.Surface, term: float | int) -> pygame.Surface:
    return pygame.transform.scale(
        img, (img.get_width() + term, img.get_height() + term)
    )
