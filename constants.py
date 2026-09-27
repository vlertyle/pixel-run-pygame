# All game constants in one place

# Screen
SCREEN_W = 800
SCREEN_H = 450
FPS = 60

# Physics
GRAVITY = 0.55
JUMP_VEL = -13.5
PLAYER_SPEED = 4.5
MAX_FALL = 16

# Colours  (R, G, B)
SKY_TOP       = (26, 10, 46)
SKY_MID       = (45, 27, 105)
SKY_BOT       = (74, 35, 90)
GRASS_TOP     = (39, 174, 96)
DIRT          = (139, 69, 19)
DIRT_DARK     = (122, 59, 14)
GROUND_SHADE  = (30, 132, 73)

CLOUD_COLOR   = (255, 255, 255, 216)

PLAYER_BODY   = (124, 92, 191)
PLAYER_HEAD   = (244, 194, 125)
PLAYER_HAIR   = (59, 35, 20)
PLAYER_SCARF  = (231, 76, 60)
PLAYER_PANTS  = (44, 62, 80)
PLAYER_SHOE1  = (139, 0, 0)
PLAYER_SHOE2  = (192, 57, 43)

ENEMY_MUSH_BODY = (142, 68, 173)
ENEMY_MUSH_CAP  = (192, 57, 43)
ENEMY_SPIKE_BODY = (44, 62, 80)
ENEMY_SPIKE_SPIK = (231, 76, 60)

COIN_OUTER  = (241, 196, 15)
COIN_INNER  = (243, 156, 18)
COIN_SIZE   = 16          # collision box of a coin (width and height)

FLAG_POLE   = (189, 195, 199)
FLAG_CLOTH  = (46, 204, 113)
FLAG_STAR   = (241, 196, 15)

HUD_BG      = (0, 0, 0, 102)
HUD_TEXT    = (255, 255, 255)

# Scores
SCORE_COIN     = 10
SCORE_ENEMY    = 100
SCORE_FLAG     = 500

# Levels
MAX_LEVEL = 4
BOSS_LEVEL = 4

LEVEL_NAMES = {
    1: "EASY",
    2: "MEDIUM",
    3: "HARD",
    4: "BOSS FIGHT",
}

# Boss fight
BOSS_MAX_HP = 6
BOSS_BODY       = (192, 57, 43)
BOSS_BODY_DARK  = (120, 30, 25)
BOSS_EYE        = (241, 196, 15)
BOSS_SPIKE      = (44, 62, 80)
BOSS_PROJECTILE = (231, 76, 60)
SCORE_BOSS = 1000
