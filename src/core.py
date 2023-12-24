import pygame
from pygame._sdl2 import Window

from src import shared
from src.states import StateManager
from src.wallpapers import get_windows_wallpaper


class Core:
    def __init__(self) -> None:
        self.win_init()
        self.state_manager = StateManager()
        self.create_blur()

    def win_init(self):
        shared.screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE)
        shared.srect = shared.screen.get_rect()
        self.clock = pygame.time.Clock()

        window = Window.from_display_module()
        window.opacity = 0.9

    def create_blur(self):
        return
        self.blur_effect = pygame.image.load(get_windows_wallpaper()).convert()
        self.blur_effect = pygame.transform.gaussian_blur(self.blur_effect, 10)

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
