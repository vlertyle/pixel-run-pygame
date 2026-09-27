# player.py
# ─────────────────────────────────────────
# Player entity: input handling, physics, collision, animation state.

import pygame
from constants import (
    GRAVITY, JUMP_VEL, PLAYER_SPEED, MAX_FALL,
    SCREEN_W, SCREEN_H,
)
from sprites import draw_player


class Player:
    # Hitbox
    W = 28
    H = 40

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.jumps = 0          # 0 = can jump, 1 = used first, 2 = used double
        self._jump_held = False  # prevents holding space for infinite jump
        self.direction = 1       # 1 = right, -1 = left
        self.state = 'idle'      # 'idle' | 'run' | 'jump'
        self.invincible = 0      # frames of invincibility after being hit

    # Input and physics
    def update(self, keys, platforms: list[dict]):
        self._handle_input(keys)
        self._apply_physics()
        self._collide_platforms(platforms)
        self._update_state()
        self._clamp_to_screen()
        if self.invincible > 0:
            self.invincible -= 1

    def _handle_input(self, keys):
        left  = keys[pygame.K_LEFT]  or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump  = keys[pygame.K_UP]    or keys[pygame.K_w] or keys[pygame.K_SPACE]

        if left:
            self.vx = -PLAYER_SPEED
            self.direction = -1
        elif right:
            self.vx = PLAYER_SPEED
            self.direction = 1
        else:
            self.vx *= 0.75  # friction

        if jump:
            if not self._jump_held and self.jumps < 2:
                self.vy = JUMP_VEL if self.jumps == 0 else JUMP_VEL * 0.9
                self.jumps += 1
                self._jump_held = True
        else:
            self._jump_held = False

    def _apply_physics(self):
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        self.x += self.vx
        self.y += self.vy

    def _collide_platforms(self, platforms: list[dict]):
        self.on_ground = False
        bottom = self.y + self.H

        for plat in platforms:
            pw = plat['w']
            px, py = plat['x'], plat['y']

            # Only resolve landing (falling downward, feet entering top of platform)
            if (self.x + self.W > px and
                    self.x + 4 < px + pw and
                    bottom > py and
                    bottom < py + 20 and
                    self.vy >= 0):
                self.y = py - self.H
                self.vy = 0.0
                self.on_ground = True
                self.jumps = 0

    def _update_state(self):
        if not self.on_ground:
            self.state = 'jump'
        elif abs(self.vx) > 0.5:
            self.state = 'run'
        else:
            self.state = 'idle'

    def _clamp_to_screen(self):
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_W - self.W:
            self.x = SCREEN_W - self.W

    # Hit detection helpers
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def is_dead(self) -> bool:

        return self.y > SCREEN_H + 60

    def take_hit(self):

        self.invincible = 90
        self.vy = JUMP_VEL * 0.5

    def bounce(self):

        self.vy = JUMP_VEL * 0.65

    # Rendering
    def draw(self, surf, frame: int):
        # Blink while invincible
        if self.invincible > 0 and (self.invincible // 6) % 2 == 1:
            return  # skip this frame → creates blink effect
        draw_player(surf, int(self.x), int(self.y),
                    self.direction, frame, self.state, self.invincible)
