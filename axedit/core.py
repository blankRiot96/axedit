import platform

import pygame
from pygame._sdl2 import Window

from axedit import shared
from axedit.autocompletions import AutoCompletions
from axedit.funcs import get_icon, set_windows_title, set_windows_title_bar_color
from axedit.logs import logger
from axedit.states import StateManager
from axedit.themes import apply_theme


def true_exit():
    logger.debug("EXIT CALLED")
    shared.running = False
    shared.client_socket.close()
    shared.server_process.kill()


__builtins__["exit"] = true_exit


class Core:
    def __init__(self) -> None:
        apply_theme("catppuccin-mocha")
        self.win_init()
        self.shared_refresh()
        shared.action_queue = []
        self.state_manager = StateManager()
        self.frame_no = 0
        shared.autocompletion = AutoCompletions()
        logger.debug("CORE INITIALIZED")

    def win_init(self):
        shared.screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE, vsync=1)
        shared.srect = shared.screen.get_rect()
        shared.frame_cache = {}
        self.clock = pygame.Clock()
        window = Window.from_display_module()
        window.opacity = 0.9

        icon = get_icon(shared.theme["default-fg"])
        pygame.display.set_icon(icon)

        pygame.display.set_caption(shared.APP_NAME)
        if platform.system() == "Windows":
            set_windows_title_bar_color()
            set_windows_title()

    def event_handler(self):
        for event in shared.events:
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.VIDEORESIZE:
                shared.srect = shared.screen.get_rect()

    def shared_refresh(self):
        shared.frame_cache.clear()
        shared.events = pygame.event.get()
        shared.dt = self.clock.tick() / 1000
        shared.dt = min(shared.dt, 0.1)
        shared.keys = pygame.key.get_pressed()
        shared.kp = pygame.key.get_just_pressed()
        shared.kr = pygame.key.get_just_released()
        shared.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        shared.theme_changed = False
        shared.mouse_press = pygame.mouse.get_pressed()

    def update(self):
        self.shared_refresh()
        self.event_handler()
        self.state_manager.update()
        if shared.theme_changed:
            if platform.system == "Windows":
                set_windows_title_bar_color()
            pygame.display.set_icon(get_icon(shared.theme["default-fg"]))
        # pygame.display.set_caption(f"{self.clock.get_fps():.0f}")

    def draw(self):
        shared.screen.fill(shared.theme["default-bg"])
        # shared.screen.blit(self.blur_effect, (0, 0))
        self.state_manager.draw()
        pygame.display.flip()

    def run(self):
        while shared.running:
            self.update()
            self.draw()
