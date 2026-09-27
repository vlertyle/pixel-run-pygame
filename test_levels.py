"""Tests for the level generation of Pixel Run.

These tests cover the layout logic only, so they need no display and no
pygame window. The first two tests are the regression tests for the bug
where coins on level 3 were placed outside their platform and partly off
the screen, which made the level impossible to complete.

Run:  python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import BOSS_LEVEL, COIN_SIZE, MAX_LEVEL, SCREEN_W  # noqa: E402
from levels import (  # noqa: E402
    MIN_ENEMY_PLATFORM_W,
    coins_per_platform,
    get_coins,
    get_enemies,
    get_flag_pos,
    get_platforms,
)

PLAYABLE_LEVELS = [1, 2, 3]


class CoinPlacementTest(unittest.TestCase):
    def test_every_coin_stays_on_screen(self):
        for level in PLAYABLE_LEVELS:
            for coin in get_coins(get_platforms(level), level):
                with self.subTest(level=level, x=coin['x']):
                    self.assertGreaterEqual(coin['x'], 0)
                    self.assertLessEqual(coin['x'] + COIN_SIZE, SCREEN_W)

    def test_every_coin_sits_above_its_platform(self):
        """Regression test: on level 3 the third coin used to hang over the edge."""
        for level in PLAYABLE_LEVELS:
            platforms = get_platforms(level)[1:]
            for coin in get_coins(get_platforms(level), level):
                on_platform = any(
                    plat['x'] <= coin['x'] and coin['x'] + COIN_SIZE <= plat['x'] + plat['w']
                    for plat in platforms
                )
                with self.subTest(level=level, x=coin['x']):
                    self.assertTrue(on_platform)

    def test_narrow_platforms_get_fewer_coins(self):
        self.assertEqual(coins_per_platform(160), 3)
        self.assertEqual(coins_per_platform(55), 2)
        self.assertEqual(coins_per_platform(40), 1)

    def test_coins_on_the_same_platform_do_not_overlap(self):
        for level in PLAYABLE_LEVELS:
            platforms = get_platforms(level)
            ground = platforms[0]
            for plat in platforms[1:]:
                coins = sorted(c['x'] for c in get_coins([ground, plat], level))
                for left, right in zip(coins, coins[1:]):
                    with self.subTest(level=level, platform=plat['x'], left=left):
                        self.assertGreaterEqual(right - left, COIN_SIZE)

    def test_every_level_has_coins_to_collect(self):
        for level in PLAYABLE_LEVELS:
            self.assertGreater(len(get_coins(get_platforms(level), level)), 0)

    def test_boss_level_has_no_coins(self):
        self.assertEqual(get_coins(get_platforms(BOSS_LEVEL), BOSS_LEVEL), [])


class EnemyPlacementTest(unittest.TestCase):
    def test_every_level_has_enemies(self):
        """Level 3 used to end up with no enemies at all because of a width filter."""
        for level in PLAYABLE_LEVELS:
            with self.subTest(level=level):
                self.assertGreater(len(get_enemies(get_platforms(level), level)), 0)

    def test_enemies_patrol_within_their_platform(self):
        for level in PLAYABLE_LEVELS:
            for enemy in get_enemies(get_platforms(level), level):
                with self.subTest(level=level, x=enemy['x']):
                    self.assertGreaterEqual(enemy['x'], enemy['plat_x'])
                    self.assertLessEqual(enemy['x'], enemy['plat_x'] + enemy['plat_w'])
                    self.assertGreaterEqual(enemy['plat_w'], MIN_ENEMY_PLATFORM_W)

    def test_enemies_get_faster_on_higher_levels(self):
        speed_1 = abs(get_enemies(get_platforms(1), 1)[0]['vx'])
        speed_3 = abs(get_enemies(get_platforms(3), 3)[0]['vx'])
        self.assertGreater(speed_3, speed_1)

    def test_boss_level_has_no_regular_enemies(self):
        self.assertEqual(get_enemies(get_platforms(BOSS_LEVEL), BOSS_LEVEL), [])


class PlatformTest(unittest.TestCase):
    def test_first_platform_is_the_ground(self):
        for level in range(1, MAX_LEVEL + 1):
            ground = get_platforms(level)[0]
            with self.subTest(level=level):
                self.assertEqual(ground['x'], 0)
                self.assertGreaterEqual(ground['w'], SCREEN_W)

    def test_platforms_start_inside_the_screen(self):
        for level in range(1, MAX_LEVEL + 1):
            for plat in get_platforms(level)[1:]:
                with self.subTest(level=level, x=plat['x']):
                    self.assertGreaterEqual(plat['x'], 0)
                    self.assertLessEqual(plat['x'] + plat['w'], SCREEN_W)

    def test_unknown_level_falls_back_to_the_last_layout(self):
        self.assertEqual(get_platforms(99), get_platforms(MAX_LEVEL))

    def test_flag_is_inside_the_screen(self):
        for level in PLAYABLE_LEVELS:
            x, y = get_flag_pos(level)
            with self.subTest(level=level):
                self.assertTrue(0 < x < SCREEN_W)
                self.assertGreater(y, 0)


if __name__ == "__main__":
    unittest.main()
