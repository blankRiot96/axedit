import pygame

from src import shared
from src.states import StateManager


class Core:
    def __init__(self) -> None:
        self.win_init()
        self.state_manager = StateManager()

    def win_init(self):
        shared.screen = pygame.display.set_mode((1100, 650))
        shared.srect = shared.screen.get_rect()
        self.clock = pygame.time.Clock()

    def update(self):
        shared.events = pygame.event.get()
        shared.dt = self.clock.tick(60) / 1000
        shared.keys = pygame.key.get_pressed()
        for event in shared.events:
            if event.type == pygame.QUIT:
                exit()

        self.state_manager.update()

    def draw(self):
        shared.screen.fill("black")
        self.state_manager.draw()
        pygame.display.update()

    def run(self):
        while True:
            self.update()
            self.draw()
