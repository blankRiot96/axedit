import html

import pygame
import pygame_gui

pygame.init()
screen = pygame.display.set_mode((480, 320))
manager = pygame_gui.UIManager((480, 320))
pygame.display.set_caption("My Board")

text = pygame_gui.elements.UITextEntryBox(pygame.Rect(0, 0, 480, 320), manager=manager)


def escape(text: str) -> str:
    return html.escape(text).encode("ascii", "xmlcharrefreplace").decode()


clock = pygame.Clock()
exit = False
while not exit:
    dt = clock.tick() / 1000
    for event in pygame.event.get():
        manager.process_events(event)
        if event.type == pygame.QUIT:
            exit = True
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            pass

    manager.update(dt)

    screen.fill("black")
    manager.draw_ui(screen)
    pygame.display.update()
