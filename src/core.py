import itertools
import os

import keyboard
import pygame
from pygame._sdl2 import Window

from src import shared
from src.states import StateManager
from src.wallpapers import get_windows_wallpaper

# TERMINAL_PATH = "C:/Program Files/WindowsApps/Microsoft.WindowsTerminal_1.18.3181.0_x64__8wekyb3d8bbwe/WindowsTerminal.exe"
TERMINAL_PATH = "C:\Program Files\WindowsApps\Microsoft.WindowsTerminal_1.18.3181.0_x64__8wekyb3d8bbwe\wt.exe"

import psutil
import pygetwindow as gw


def focus_on_application(file_path):
    # Get the process ID of the application based on the file path
    process_id = None
    for process in psutil.process_iter(["pid", "name", "exe"]):
        if process.info["exe"] and file_path.lower() in process.info["exe"].lower():
            process_id = process.info["pid"]
            break

    if process_id is not None:
        # Bring the application window to the front
        window = gw.getWindowsWithTitle("")[
            0
        ]  # You can replace "" with the title of your application window
        window.activate()
        print(f"Focused on the application with file path: {file_path}")
    else:
        print(f"Application with file path {file_path} not found.")


class Core:
    def __init__(self) -> None:
        self.win_init()
        self.state_manager = StateManager()
        self.create_blur()

        keyboard.add_hotkey("ctrl+grave", self.on_terminal_switch)
        self.titles = itertools.cycle(("PowerShell", "axedit"))

    def win_init(self):
        shared.screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE)
        shared.srect = shared.screen.get_rect()
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("axedit")

        window = Window.from_display_module()
        window.opacity = 0.9

    def create_blur(self):
        return
        self.blur_effect = pygame.image.load(get_windows_wallpaper()).convert()
        self.blur_effect = pygame.transform.gaussian_blur(self.blur_effect, 10)

    # TODO: Fix pygetwindow.PyGetWindowException: Error code from Windows: 0
    # - The operation completed successfully.
    # * Occurs when switching from terminal to app
    def on_terminal_switch(self):
        window = gw.getWindowsWithTitle(next(self.titles))
        window[0].activate()

    def update(self):
        shared.events = pygame.event.get()
        shared.dt = self.clock.tick(60) / 1000
        shared.dt = min(shared.dt, 0.1)
        shared.keys = pygame.key.get_pressed()
        for event in shared.events:
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.VIDEORESIZE:
                shared.srect = shared.screen.get_rect()
                self.create_blur()

        self.state_manager.update()
        # pygame.display.set_caption(f"{self.clock.get_fps()}")

    def draw(self):
        shared.screen.fill("black")
        # shared.screen.blit(self.blur_effect, (0, 0))
        self.state_manager.draw()
        pygame.display.update()

    def run(self):
        while True:
            self.update()
            self.draw()
