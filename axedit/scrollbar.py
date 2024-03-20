import pygame

from axedit import shared
from axedit.logs import logger


class HorizontalScrollBar:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, 100, 20)
        self.surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.surf.fill(shared.theme["dark-fg"])
        self.alpha = 0
        self.alpha_rise = False
        self.fade_speed = 300
        self.zero_pos = 0

    def handle_alpha(self):
        self.alpha_rise = shared.mouse_pos.y > self.rect.y - 10
        shared.handling_scroll_bar = self.alpha_rise

        if self.alpha_rise:
            self.alpha += self.fade_speed * shared.dt
            if self.alpha > 255:
                self.alpha = 255
        else:
            self.alpha -= self.fade_speed * shared.dt
            if self.alpha < 0:
                self.alpha = 0

    def handle_scroll(self):
        if not shared.mouse_press[0]:
            return

        self.rect.centerx = shared.mouse_pos.x

    def bound_bar(self):
        if self.rect.x < self.zero_pos:
            self.rect.x = self.zero_pos
        elif self.rect.x > shared.srect.width - self.rect.width:
            self.rect.x = shared.srect.width - self.rect.width

    def apply_scroll(self):
        max_scroll_x = len(max(shared.chars)) * shared.FONT_WIDTH
        shared.scroll.x = max_scroll_x * (
            (self.rect.x - self.zero_pos)
            / (shared.srect.width - self.rect.width - self.zero_pos)
        )

    def update(self):
        self.handle_alpha()
        self.handle_scroll()
        self.bound_bar()
        self.apply_scroll()

    def draw(self):
        self.surf.set_alpha(self.alpha)
        shared.screen.blit(self.surf, self.rect)
