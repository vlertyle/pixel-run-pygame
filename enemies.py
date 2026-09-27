# Enemy entities.
#   type 0 - mushroom walker
#   type 1 - spike ball

import pygame
from sprites import draw_enemy_mushroom, draw_enemy_spike


class Enemy:
    W = 28
    H = 32

    def __init__(self, data: dict):
        self.x      = float(data['x'])
        self.y      = float(data['y'])
        self.vx     = float(data['vx'])
        self.plat_x = int(data['plat_x'])
        self.plat_w = int(data['plat_w'])
        self.etype  = int(data['type'])   # 0 = mushroom, 1 = spike
        self.alive  = True

    # Update
    def update(self):
        if not self.alive:
            return
        self.x += self.vx
        # Bounce off platform edges
        if self.x <= self.plat_x or self.x + self.W >= self.plat_x + self.plat_w:
            self.vx *= -1

    # Collision helpers
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) + 4, int(self.y) + 4,
                           self.W - 8, self.H - 4)

    # Rendering
    def draw(self, surf, frame: int):
        if not self.alive:
            return
        if self.etype == 0:
            draw_enemy_mushroom(surf, int(self.x), int(self.y), frame)
        else:
            draw_enemy_spike(surf, int(self.x), int(self.y), frame)
