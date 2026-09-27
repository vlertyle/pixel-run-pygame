# levels.py
# ─────────────────────────────────────────
# Platform, coin and enemy layouts for every level.

from constants import BOSS_LEVEL, COIN_SIZE, SCREEN_H, SCREEN_W

# Free space kept between a coin and the edge of its platform
COIN_MARGIN = 6

# Minimum platform width an enemy needs in order to patrol
MIN_ENEMY_PLATFORM_W = 45


def get_platforms(level: int) -> list[dict]:
    """Return the platform list for the given level (1-indexed).

    Each dict: { 'x': int, 'y': int, 'w': int }
    The ground platform (full width) is always index 0.
    """
    ground = {'x': 0, 'y': SCREEN_H - 50, 'w': SCREEN_W + 10}

    layouts = [
        # Level 1 – EASY: wide platforms, small gaps, low jumps
        [
            {'x':  90, 'y': 360, 'w': 160},
            {'x': 300, 'y': 340, 'w': 150},
            {'x': 500, 'y': 360, 'w': 150},
            {'x': 680, 'y': 330, 'w': 110},
            {'x': 240, 'y': 250, 'w': 110},
            {'x': 460, 'y': 230, 'w': 100},
        ],
        # Level 2 – MEDIUM: smaller platforms, bigger gaps, more height variation
        [
            {'x':  60, 'y': 360, 'w': 100},
            {'x': 200, 'y': 310, 'w':  80},
            {'x': 310, 'y': 250, 'w': 100},
            {'x': 450, 'y': 300, 'w':  70},
            {'x': 550, 'y': 220, 'w': 120},
            {'x': 690, 'y': 280, 'w':  80},
            {'x': 140, 'y': 180, 'w':  70},
            {'x': 380, 'y': 160, 'w':  60},
        ],
        # Level 3 – HARD: narrow platforms, long gaps, precise jumps.
        # The former platform at x=760 touched the right screen edge, so the
        # coins on it ended up outside the visible area. It now starts at 740.
        [
            {'x':  50, 'y': 380, 'w':  60},
            {'x': 160, 'y': 330, 'w':  55},
            {'x': 260, 'y': 270, 'w':  55},
            {'x': 370, 'y': 220, 'w':  50},
            {'x': 470, 'y': 270, 'w':  55},
            {'x': 580, 'y': 220, 'w':  55},
            {'x': 690, 'y': 280, 'w':  60},
            {'x': 740, 'y': 200, 'w':  50},
            {'x': 100, 'y': 170, 'w':  50},
            {'x': 320, 'y': 140, 'w':  50},
        ],
        # Level 4 – BOSS ARENA: open space with two side platforms to dodge from
        [
            {'x': 100, 'y': 330, 'w': 120},
            {'x': 580, 'y': 330, 'w': 120},
        ],
    ]

    idx = min(level - 1, len(layouts) - 1)
    return [ground] + layouts[idx]


def coins_per_platform(width: int) -> int:
    """How many coins fit on a platform of this width.

    Narrow platforms (level 3) get fewer coins. Previously every platform
    received three coins regardless of its width, so the last coin was
    pushed past the platform edge - and on the rightmost platform even off
    the screen, which made a full collection of level 3 impossible.
    """
    if width >= 90:
        return 3
    if width >= 50:
        return 2
    return 1


def get_coins(platforms: list[dict], level: int = 1) -> list[dict]:
    """Place coins above every non-ground platform.

    Each dict: { 'x': float, 'y': float, 'collected': bool }
    Coins are spread evenly across the platform and always stay inside both
    the platform and the screen. The boss level has no coins.
    """
    if level >= BOSS_LEVEL:
        return []

    coins = []
    for plat in platforms[1:]:  # skip the ground
        count = coins_per_platform(plat['w'])
        first_x = plat['x'] + COIN_MARGIN
        usable = plat['w'] - 2 * COIN_MARGIN - COIN_SIZE
        step = usable / (count - 1) if count > 1 else 0

        for i in range(count):
            x = first_x + i * step
            x = max(0, min(x, SCREEN_W - COIN_SIZE))  # never leave the screen
            coins.append({
                'x': float(x),
                'y': float(plat['y'] - 30),
                'collected': False,
            })
    return coins


def get_enemies(platforms: list[dict], level: int) -> list[dict]:
    """Place an enemy on every other platform that is wide enough to patrol.

    Each dict: { 'x', 'y', 'vx', 'plat_x', 'plat_w', 'type' }
    type 0 = mushroom, type 1 = spike ball.
    The boss level has no regular enemies - the boss is the only threat.
    """
    if level >= BOSS_LEVEL:
        return []

    enemies = []
    speed = 0.7 + level * 0.35

    for i, plat in enumerate(platforms[1:]):
        if i % 2 == 0 and plat['w'] >= MIN_ENEMY_PLATFORM_W:
            direction = 1 if (i % 4 < 2) else -1
            enemies.append({
                'x':      float(plat['x'] + 8),
                'y':      float(plat['y'] - 36),
                'vx':     direction * speed,
                'plat_x': plat['x'],
                'plat_w': plat['w'],
                'type':   1 if (i % 3 == 0) else 0,
            })
    return enemies


def get_flag_pos(level: int) -> tuple[int, int]:
    """Return the (x, y) top-left corner of the goal flag for this level.

    The boss level has no flag - it is won by defeating the boss.
    """
    positions = {
        1: (730, SCREEN_H - 175),
        2: (730, SCREEN_H - 175),
        3: (730, SCREEN_H - 175),
    }
    return positions.get(level, (730, SCREEN_H - 175))
