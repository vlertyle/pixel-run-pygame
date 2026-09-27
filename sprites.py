# sprites.py
# ─────────────────────────────────────────
# Procedural pixel-art drawing functions.
# Every draw_* function receives a pygame Surface and draws directly onto it.

import math
import pygame
from constants import (
    BOSS_BODY, BOSS_BODY_DARK, BOSS_EYE, BOSS_PROJECTILE, BOSS_SPIKE,
    CLOUD_COLOR, COIN_INNER, COIN_OUTER, DIRT, DIRT_DARK,
    ENEMY_MUSH_BODY, ENEMY_MUSH_CAP, ENEMY_SPIKE_BODY, ENEMY_SPIKE_SPIK,
    FLAG_CLOTH, FLAG_POLE, FLAG_STAR, GRASS_TOP, GROUND_SHADE,
    PLAYER_BODY, PLAYER_HAIR, PLAYER_HEAD, PLAYER_PANTS, PLAYER_SCARF,
    PLAYER_SHOE1, PLAYER_SHOE2, SKY_BOT, SKY_MID, SKY_TOP,
)


def draw_player(surf, x, y, direction, frame, state, invincible):
    # Offsets so we draw relative to centre-bottom of sprite
    cx, cy = x + 16, y + 20

    # Shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 45), (cx - 12, cy + 19, 24, 8))

    run_phase = (frame // 8) % 2

    def block(color, rx, ry, rw, rh):
        if direction < 0:
            rx = -rx - rw  # mirror
        pygame.draw.rect(surf, color, (cx + rx, cy + ry, rw, rh))

    # Body
    block(PLAYER_BODY, -9, -2, 18, 14)

    # Head
    block(PLAYER_HEAD, -8, -18, 16, 14)

    # Hair
    block(PLAYER_HAIR, -8, -18, 16, 5)
    block(PLAYER_HAIR, -10, -14, 3, 8)
    block(PLAYER_HAIR,  7, -14, 3, 5)

    # Eyes
    block((26, 26, 46),  -5, -12, 3, 3)
    block((26, 26, 46),   2, -12, 3, 3)
    # Shine
    block((255, 255, 255), -4, -12, 1, 1)
    block((255, 255, 255),  3, -12, 1, 1)

    # Mouth
    block((192, 57, 43), -3, -7, 6, 2)

    # Scarf
    block(PLAYER_SCARF, -9, -3, 18, 4)

    # Pants
    block(PLAYER_PANTS, -9, 12, 18, 8)

    # Legs and shoes
    if state == 'jump':
        block(PLAYER_PANTS, -8, 20, 6, 6)
        block(PLAYER_PANTS,  2, 20, 6, 6)
        block(PLAYER_SHOE2, -9, 24, 7, 4)
        block(PLAYER_SHOE1,  2, 24, 7, 4)
    elif run_phase == 0:
        block(PLAYER_PANTS, -8, 20, 6, 9)
        block(PLAYER_PANTS,  2, 20, 6, 6)
        block(PLAYER_SHOE1, -9, 28, 7, 4)
        block(PLAYER_SHOE2,  1, 24, 8, 4)
    else:
        block(PLAYER_PANTS, -8, 20, 6, 6)
        block(PLAYER_PANTS,  2, 20, 6, 9)
        block(PLAYER_SHOE2, -9, 24, 8, 4)
        block(PLAYER_SHOE1,  1, 28, 7, 4)

    # Arms
    arm_color = (106, 79, 172)
    if state == 'jump':
        block(arm_color, -14, -2,  5, 10)
        block(arm_color,   9, -5,  5, 10)
    else:
        block(arm_color, -14, 0, 5, 12)
        block(arm_color,   9, 0, 5, 12)


def draw_enemy_mushroom(surf, x, y, frame):
    cx, cy = x + 16, y + 16
    bob = int(math.sin(frame * 0.1) * 2)
    cy += bob

    # Body
    pygame.draw.rect(surf, ENEMY_MUSH_BODY, (cx - 12, cy, 24, 14))

    # Cap
    cap_pts = []
    for i in range(13):
        angle = math.pi * i / 12
        cap_pts.append((cx + int(13 * math.cos(math.pi - angle)),
                         cy - 2 + int(13 * math.sin(math.pi - angle))))
    pygame.draw.polygon(surf, ENEMY_MUSH_CAP, cap_pts)

    # Spots
    pygame.draw.rect(surf, (250, 219, 216), (cx - 8, cy - 12, 5, 5))
    pygame.draw.rect(surf, (250, 219, 216), (cx + 3, cy - 8,  4, 4))

    # Eyes
    pygame.draw.rect(surf, (255, 255, 255), (cx - 7, cy + 2, 5, 5))
    pygame.draw.rect(surf, (255, 255, 255), (cx + 2, cy + 2, 5, 5))
    pygame.draw.rect(surf, (0, 0, 0),       (cx - 6, cy + 3, 3, 3))
    pygame.draw.rect(surf, (0, 0, 0),       (cx + 3, cy + 3, 3, 3))

    # Feet
    lf = (frame // 10) % 2
    pygame.draw.rect(surf, (125, 60, 152), (cx - 11 + (3 if lf else 0), cy + 14, 8, 5))
    pygame.draw.rect(surf, (125, 60, 152), (cx + 3  - (3 if lf else 0), cy + 14, 8, 5))


def draw_enemy_spike(surf, x, y, frame):
    cx, cy = x + 16, y + 16
    bob = int(math.sin(frame * 0.1) * 2)
    cy += bob

    # Spikes (drawn first so body overlaps)
    for i in range(8):
        angle = (i / 8) * math.pi * 2 + frame * 0.05
        sx = cx + int(math.cos(angle) * 15)
        sy = cy + int(math.sin(angle) * 15)
        sx2 = cx + int(math.cos(angle) * 19)
        sy2 = cy + int(math.sin(angle) * 19)
        pygame.draw.line(surf, ENEMY_SPIKE_SPIK, (sx, sy), (sx2, sy2), 4)

    # Body
    pygame.draw.circle(surf, ENEMY_SPIKE_BODY, (cx, cy), 13)

    # Face
    pygame.draw.rect(surf, (243, 156, 18), (cx - 5, cy - 4, 4, 4))
    pygame.draw.rect(surf, (243, 156, 18), (cx + 1, cy - 4, 4, 4))
    pygame.draw.rect(surf, ENEMY_SPIKE_SPIK, (cx - 4, cy + 3, 8, 3))


def draw_coin(surf, x, y, frame):
    """Animated spinning coin."""
    bob = int(math.sin(frame * 0.15) * 3)
    cx, cy = x + 8, y + 8 + bob
    w = int(8 + abs(math.sin(frame * 0.1)) * 4)

    # Outer glow
    glow = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*COIN_OUTER, 80), (16 - w - 3, 7, (w + 3) * 2, 18))
    surf.blit(glow, (cx - 16, cy - 16))

    pygame.draw.ellipse(surf, COIN_OUTER, (cx - w, cy - 9, w * 2, 18))
    pygame.draw.ellipse(surf, COIN_INNER, (cx - max(1, w - 3), cy - 6, max(2, (w - 3) * 2), 12))


def draw_flag(surf, x, y):

    # Pole
    pygame.draw.rect(surf, FLAG_POLE, (x + 12, y, 4, 120))

    # Flag cloth (triangle)
    pts = [(x + 16, y + 4), (x + 46, y + 20), (x + 16, y + 36)]
    pygame.draw.polygon(surf, FLAG_CLOTH, pts)

    # Star
    font = pygame.font.SysFont("segoeuisymbol", 14, bold=True)
    star = font.render("★", True, FLAG_STAR)
    surf.blit(star, (x + 20, y + 10))


def draw_boss(surf, x, y, frame, hp, max_hp, hit_flash):
    bob = int(math.sin(frame * 0.06) * 6)
    cx, cy = int(x), int(y) + bob

    body_color = (255, 255, 255) if hit_flash else BOSS_BODY
    dark_color = (255, 200, 200) if hit_flash else BOSS_BODY_DARK

    # Spikes around body (rotating)
    for i in range(10):
        angle = (i / 10) * math.pi * 2 + frame * 0.02
        sx = cx + int(math.cos(angle) * 34)
        sy = cy + int(math.sin(angle) * 34)
        sx2 = cx + int(math.cos(angle) * 44)
        sy2 = cy + int(math.sin(angle) * 44)
        pygame.draw.line(surf, BOSS_SPIKE, (sx, sy), (sx2, sy2), 6)

    # Main body
    pygame.draw.circle(surf, body_color, (cx, cy), 34)
    pygame.draw.circle(surf, dark_color, (cx, cy), 34, 4)

    # Eyes
    pygame.draw.circle(surf, (255, 255, 255), (cx - 13, cy - 6), 9)
    pygame.draw.circle(surf, (255, 255, 255), (cx + 13, cy - 6), 9)
    pupil_off = int(math.sin(frame * 0.05) * 3)
    pygame.draw.circle(surf, BOSS_EYE, (cx - 13 + pupil_off, cy - 6), 4)
    pygame.draw.circle(surf, BOSS_EYE, (cx + 13 + pupil_off, cy - 6), 4)

    # Angry brows
    pygame.draw.line(surf, (0, 0, 0), (cx - 20, cy - 16), (cx - 6, cy - 11), 3)
    pygame.draw.line(surf, (0, 0, 0), (cx + 20, cy - 16), (cx + 6, cy - 11), 3)

    # Mouth
    pygame.draw.arc(surf, (0, 0, 0), (cx - 16, cy + 2, 32, 20), math.pi, math.pi * 2, 3)
    # Teeth
    for tx in (-10, -2, 6, 14):
        pygame.draw.polygon(surf, (255, 255, 255),
                            [(cx + tx, cy + 5), (cx + tx + 4, cy + 5), (cx + tx + 2, cy + 11)])

    # Health bar above boss
    bar_w, bar_h = 120, 12
    bar_x, bar_y = cx - bar_w // 2, cy - 70
    pygame.draw.rect(surf, (40, 40, 40), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), border_radius=4)
    pct = max(0.0, hp / max_hp)
    fill_color = (46, 204, 113) if pct > 0.5 else (230, 126, 34) if pct > 0.25 else (192, 57, 43)
    pygame.draw.rect(surf, fill_color, (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=3)


def draw_boss_projectile(surf, x, y, frame):

    cx, cy = int(x), int(y)
    rot = frame * 0.3
    for i in range(6):
        angle = (i / 6) * math.pi * 2 + rot
        sx = cx + int(math.cos(angle) * 6)
        sy = cy + int(math.sin(angle) * 6)
        sx2 = cx + int(math.cos(angle) * 11)
        sy2 = cy + int(math.sin(angle) * 11)
        pygame.draw.line(surf, BOSS_SPIKE, (sx, sy), (sx2, sy2), 3)
    pygame.draw.circle(surf, BOSS_PROJECTILE, (cx, cy), 7)


def draw_platform(surf, x, y, w):

    # Grass top
    pygame.draw.rect(surf, GRASS_TOP, (x, y, w, 10))
    # Dirt
    pygame.draw.rect(surf, DIRT, (x, y + 10, w, 20))
    # Brick lines
    pygame.draw.rect(surf, DIRT_DARK, (x, y + 20, w, 1))
    for bx in range(x, x + w, 20):
        pygame.draw.rect(surf, DIRT_DARK, (bx, y + 10, 1, 20))
    # Edge shading
    pygame.draw.rect(surf, GROUND_SHADE, (x, y, 3, 10))
    pygame.draw.rect(surf, GROUND_SHADE, (x + w - 3, y, 3, 10))


def draw_cloud(surf, x, y):

    circles = [(x + 30, y + 20, 22), (x + 55, y + 15, 27),
               (x + 80, y + 20, 20), (x + 30, y + 28, 15), (x + 80, y + 28, 14)]
    cloud = pygame.Surface((120, 60), pygame.SRCALPHA)
    for (cx, cy, r) in circles:
        pygame.draw.circle(cloud, CLOUD_COLOR, (cx - x, cy - y), r)
    surf.blit(cloud, (x, y))


def draw_background(surf, cloud_positions, screen_w, screen_h):

    # Sky gradient (three horizontal bands)
    band_h = screen_h // 3
    for i, color in enumerate([SKY_TOP, SKY_MID, SKY_BOT]):
        pygame.draw.rect(surf, color, (0, i * band_h, screen_w, band_h + 2))

    # Stars
    star_color = (255, 255, 255)
    star_positions = [(50,30),(130,80),(200,20),(340,60),(480,25),
                      (600,70),(720,40),(770,15),(90,110),(410,100)]
    for (sx, sy) in star_positions:
        pygame.draw.rect(surf, star_color, (sx, sy, 2, 2))

    # Moon
    pygame.draw.circle(surf, (240, 232, 192), (710, 55), 28)
    pygame.draw.circle(surf, SKY_MID,          (720, 48), 22)

    # Clouds
    for (cx, cy) in cloud_positions:
        draw_cloud(surf, int(cx), int(cy))

    # Ground strip
    pygame.draw.rect(surf, GRASS_TOP, (0, screen_h - 50, screen_w, 10))
    pygame.draw.rect(surf, DIRT,      (0, screen_h - 40, screen_w, 40))
