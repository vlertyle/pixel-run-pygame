# Boss entity for Level 4.
# Moves left/right across the arena, periodically fires projectiles,
# and can be defeated by stomping it 6 times (BOSS_MAX_HP).

import math

import pygame
from constants import (
    SCREEN_W, SCREEN_H, BOSS_MAX_HP,
)
from sprites import draw_boss, draw_boss_projectile


class Projectile:
    W = H = 14

    def __init__(self, x: float, y: float, vx: float, vy: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if (self.x < -20 or self.x > SCREEN_W + 20 or
                self.y < -20 or self.y > SCREEN_H + 20):
            self.alive = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.W / 2), int(self.y - self.H / 2),
                           self.W, self.H)

    def draw(self, surf, frame: int):
        draw_boss_projectile(surf, self.x, self.y, frame)


class Boss:
    """Large boss enemy. Centre-point based positioning."""
    RADIUS = 34
    SPEED = 2.2

    def __init__(self, x: float, y: float):
        self.x = float(x)          # centre x
        self.y = float(y)          # centre y (base, bob applied visually)
        self.vx = self.SPEED
        self.hp = BOSS_MAX_HP
        self.max_hp = BOSS_MAX_HP
        self.alive = True
        self.hit_flash = 0          # frames remaining of white flash
        self.fire_cooldown = 90     # frames until next shot
        self.invuln = 0              # brief invuln after being stomped
        self.projectiles: list[Projectile] = []
        self.defeated_anim = 0       # frames into death animation

    # Update
    def update(self, player_x: float, player_y: float):
        if not self.alive:
            self.defeated_anim += 1
            return

        # Patrol back and forth within arena bounds
        self.x += self.vx
        if self.x < 130:
            self.x = 130
            self.vx *= -1
        elif self.x > SCREEN_W - 130:
            self.x = SCREEN_W - 130
            self.vx *= -1

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.invuln > 0:
            self.invuln -= 1

        # Fire projectiles periodically, aimed loosely at the player
        self.fire_cooldown -= 1
        if self.fire_cooldown <= 0:
            self._fire(player_x, player_y)
            self.fire_cooldown = max(35, 90 - (self.max_hp - self.hp) * 8)

        # Update projectiles
        for p in self.projectiles:
            p.update()
        self.projectiles = [p for p in self.projectiles if p.alive]

    def _fire(self, target_x: float, target_y: float):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(1.0, math.hypot(dx, dy))
        speed = 4.0
        vx = dx / dist * speed
        vy = dy / dist * speed
        self.projectiles.append(Projectile(self.x, self.y, vx, vy))

    # Hit handling
    def take_stomp(self):
        """Called when the player lands on top of the boss."""
        if self.invuln > 0 or not self.alive:
            return
        self.hp -= 1
        self.hit_flash = 12
        self.invuln = 45
        if self.hp <= 0:
            self.alive = False

    # Collision helpers
    def rect(self) -> pygame.Rect:
        r = self.RADIUS
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def top_rect(self) -> pygame.Rect:
        """A thinner rect across the top, used to detect stomps."""
        r = self.RADIUS
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, 18)

    # Rendering
    def draw(self, surf, frame: int):
        if self.alive:
            draw_boss(surf, self.x, self.y, frame, self.hp, self.max_hp,
                      hit_flash=(self.hit_flash > 0))
        for p in self.projectiles:
            p.draw(surf, frame)