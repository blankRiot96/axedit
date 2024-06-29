import os
import platform
from pathlib import Path

import pygame
from pygame._sdl2 import Window

from axedit import shared
from axedit.autocompletions import AutoCompletions
from axedit.debugger import Debugger
from axedit.funcs import (
    get_icon,
    safe_close_connections,
    set_windows_title,
    set_windows_title_bar_color,
    write_config,
)
from axedit.input_queue import HistoryManager
from axedit.linter import Linter
from axedit.logs import logger
from axedit.states import StateManager


def true_exit():
    logger.debug("EXIT CALLED")
    write_config()
    safe_close_connections()

    raise SystemExit


__builtins__["exit"] = true_exit


class Core:
    def __init__(self) -> None:
        self.win_init()
        self.shared_frame_refresh()
        shared.action_queue = []
        self.state_manager = StateManager()
        self.frame_no = 0
        shared.autocompletion = AutoCompletions()
        shared.linter = Linter()
        self.debugger = Debugger()
        shared.history = HistoryManager()
        logger.debug("CORE INITIALIZED")

    def win_init(self):
        shared.screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE, vsync=1)
        shared.srect = shared.screen.get_rect()
        shared.frame_cache = {}
        shared.clock = pygame.Clock()
        window = Window.from_display_module()
        window.opacity = float(shared.config["opacity"]["value"])

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

    def shared_frame_refresh(self):
        shared.frame_cache.clear()
        shared.events = pygame.event.get()
        shared.dt = shared.clock.tick() / 1000
        shared.dt = min(shared.dt, 0.1)
        shared.keys = pygame.key.get_pressed()
        shared.kp = pygame.key.get_just_pressed()
        shared.kr = pygame.key.get_just_released()
        shared.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        shared.theme_changed = False
        shared.mouse_press = pygame.mouse.get_pressed()

    def on_ctrl_question(self):
        if not (
            shared.keys[pygame.K_LCTRL]
            and shared.keys[pygame.K_LSHIFT]
            and shared.kp[pygame.K_SLASH]
        ):
            return

        pygame.image.save(shared.screen, Path("/home/axis/p/editor/showcase.png"))
        query = "convert ~/p/editor/showcase.png \( +clone -background black -shadow 50x10+15+15 \) +swap -background none -layers merge +repage ~/p/editor/showcase.png"
        os.system(query)
        logger.debug("Showcased screenshot")

    def update(self):
        self.shared_frame_refresh()
        self.event_handler()
        self.state_manager.update()
        if shared.theme_changed:
            if platform.system == "Windows":
                set_windows_title_bar_color()
            pygame.display.set_icon(get_icon(shared.theme["default-fg"]))

        self.on_ctrl_question()
        self.debugger.update()
        # pygame.display.set_caption(f"{self.clock.get_fps():.0f}")

    def draw(self):
        shared.screen.fill(shared.theme["default-bg"])
        # shared.screen.blit(self.blur_effect, (0, 0))
        self.state_manager.draw()
        # self.debugger.draw()
        pygame.display.flip()

    def run(self):
        while shared.running:
            self.update()
            self.draw()
