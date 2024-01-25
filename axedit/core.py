import os
import platform

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from pygame._sdl2 import Window

from axedit import shared
from axedit.funcs import get_icon, set_windows_title
from axedit.states import StateManager


class Core:
    def __init__(self) -> None:
        self.win_init()
        self.state_manager = StateManager()
        self.frame_no = 0
        shared.action_queue = []

    def win_init(self):
        shared.screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE, vsync=1)
        shared.srect = shared.screen.get_rect()
        self.clock = pygame.time.Clock()
        shared.frame_cache = {}
        window = Window.from_display_module()
        window.opacity = 0.9

        icon = get_icon()
        pygame.display.set_icon(icon)

        pygame.display.set_caption(shared.APP_NAME)
        if platform.system() == "Windows":
            from ctypes import byref, c_int, sizeof, windll

            info = pygame.display.get_wm_info()
            HWND = info["window"]

            title_bar_color = 0x00000000
            windll.dwmapi.DwmSetWindowAttribute(
                HWND, 35, byref(c_int(title_bar_color)), sizeof(c_int)
            )

            set_windows_title()

    def event_handler(self):
        for event in shared.events:
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.VIDEORESIZE:
                shared.srect = shared.screen.get_rect()
                set_windows_title()
            elif event.type == pygame.TEXTINPUT:
                shared.action_queue.append(event.text)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    shared.action_queue.append("ctrl")
                elif event.key in (pygame.K_LALT, pygame.K_RALT):
                    shared.action_queue.append("alt")

    def shared_refresh(self):
        shared.frame_cache.clear()
        shared.events = pygame.event.get()
        shared.dt = self.clock.tick() / 1000
        shared.dt = min(shared.dt, 0.1)
        shared.keys = pygame.key.get_pressed()
        shared.kp = pygame.key.get_just_pressed()
        shared.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

    def update(self):
        self.shared_refresh()
        self.event_handler()
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
