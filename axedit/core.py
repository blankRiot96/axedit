from ctypes import byref, c_int, sizeof, windll

import pygame
from pygame._sdl2 import Window

from axedit import shared
from axedit.states import StateManager


class Core:
    def __init__(self) -> None:
        self.win_init()
        self.state_manager = StateManager()
        self.frame_no = 0

    def win_init(self):
        shared.screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE, vsync=1)
        shared.srect = shared.screen.get_rect()
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("axedit")
        shared.frame_cache = {}

        window = Window.from_display_module()
        window.opacity = 0.9

        info = pygame.display.get_wm_info()
        HWND = info["window"]
        title_bar_color = 0x00000000
        windll.dwmapi.DwmSetWindowAttribute(
            HWND, 35, byref(c_int(title_bar_color)), sizeof(c_int)
        )

    def update(self):
        shared.frame_cache.clear()
        shared.events = pygame.event.get()
        shared.dt = self.clock.tick() / 1000
        shared.dt = min(shared.dt, 0.1)
        shared.keys = pygame.key.get_pressed()
        shared.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        for event in shared.events:
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.VIDEORESIZE:
                shared.srect = shared.screen.get_rect()
        self.state_manager.update()
        pygame.display.set_caption(f"{self.clock.get_fps():.0f}")

    def draw(self):
        shared.screen.fill("black")
        # shared.screen.blit(self.blur_effect, (0, 0))
        self.state_manager.draw()
        pygame.display.flip()

    def run(self):
        while True:
            self.update()
            self.draw()
