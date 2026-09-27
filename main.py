import sys

import pygame

from constants import FPS, SCREEN_H, SCREEN_W
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption("Pixel Run")

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    game = Game(screen)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update()
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()