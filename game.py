# Top-level Game class.
# Manages: state machine, level loading, HUD, menus, all entity updates.

import pygame
from constants import (
    SCREEN_W, SCREEN_H, MAX_LEVEL, BOSS_LEVEL,
    SCORE_COIN, SCORE_ENEMY, SCORE_FLAG, SCORE_BOSS,
    LEVEL_NAMES, COIN_SIZE, HUD_BG, HUD_TEXT,
)
from levels   import get_platforms, get_coins, get_enemies, get_flag_pos
from player   import Player
from enemies  import Enemy
from boss     import Boss
from sprites  import (draw_background, draw_platform,
                      draw_coin, draw_flag)


# Simple UI helpers
def _make_font(size, bold=False):
    for name in ("Courier New", "couriernew", "monospace"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)


class Game:
    # States
    MENU    = 'menu'
    PLAYING = 'playing'
    DEAD    = 'dead'       # brief pause before respawn
    GAMEOVER= 'gameover'
    WIN     = 'win'

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state  = self.MENU
        self.frame  = 0

        # Persistent across levels / deaths
        self.score = 0
        self.lives = 5
        self.level = 1

        # Cloud positions (world-space, float for smooth scroll)
        self.clouds = [[60.0, 40], [320.0, 25], [580.0, 55], [700.0, 30]]

        # Fonts
        self.font_hud   = _make_font(16, bold=True)
        self.font_title = _make_font(40, bold=True)
        self.font_body  = _make_font(18)
        self.font_btn   = _make_font(22, bold=True)

        # Dead-pause timer
        self._dead_timer = 0

        # Level objects (populated by _init_level)
        self.platforms : list[dict]   = []
        self.coins     : list[dict]   = []
        self.enemies   : list[Enemy]  = []
        self.player    : Player | None = None
        self.flag_pos  : tuple[int,int] = (730, 0)
        self.flag_done  = False
        self.boss      : Boss | None = None   # only set on boss level

    # Level setup
    def _init_level(self):
        self.platforms = get_platforms(self.level)
        self.coins     = get_coins(self.platforms, self.level)
        self.enemies   = [Enemy(d) for d in get_enemies(self.platforms, self.level)]
        self.player    = Player(60, SCREEN_H - 130)
        self.flag_pos  = get_flag_pos(self.level)
        self.flag_done = False

        if self.level == BOSS_LEVEL:
            self.boss = Boss(SCREEN_W // 2, 140)
        else:
            self.boss = None

    #Event handling
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return
        key = event.key

        if self.state == self.MENU:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_game()

        elif self.state == self.GAMEOVER:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._reset_and_start()

        elif self.state == self.WIN:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._reset_and_start()

    def _start_game(self):
        self._init_level()
        self.state = self.PLAYING

    def _reset_and_start(self):
        self.score = 0
        self.lives = 5
        self.level = 1
        self._start_game()

    # Update
    def update(self):
        self.frame += 1

        # Scroll clouds
        for c in self.clouds:
            c[0] -= 0.2
            if c[0] < -120:
                c[0] = SCREEN_W + 20

        if self.state == self.PLAYING:
            self._update_playing()
        elif self.state == self.DEAD:
            self._dead_timer -= 1
            if self._dead_timer <= 0:
                self._init_level()
                self.state = self.PLAYING

    def _update_playing(self):
        keys = pygame.key.get_pressed()
        p    = self.player

        # Player
        p.update(keys, self.platforms)

        # Fall death
        if p.is_dead():
            self.lives -= 1
            if self.lives <= 0:
                self.state = self.GAMEOVER
            else:
                self.state    = self.DEAD
                self._dead_timer = 60
            return

        # Enemies
        for e in self.enemies:
            e.update()
            if not e.alive:
                continue
            if p.invincible > 0:
                continue

            pr = p.rect()
            er = e.rect()
            if not pr.colliderect(er):
                continue

            # Stomp check
            if p.vy > 0 and p.y + p.H < e.y + e.H // 2 + 4:
                e.alive = False
                p.bounce()
                self.score += SCORE_ENEMY * self.level
            else:
                p.take_hit()
                self.lives -= 1
                if self.lives <= 0:
                    self.state = self.GAMEOVER
                return

        # Boss fight (level 4 only)
        if self.boss is not None:
            self._update_boss()
            if self.state != self.PLAYING:
                return

        # Coins
        pr = p.rect()
        for c in self.coins:
            if c['collected']:
                continue
            cr = pygame.Rect(int(c['x']), int(c['y']), COIN_SIZE, COIN_SIZE)
            if pr.colliderect(cr):
                c['collected'] = True
                self.score += SCORE_COIN

        # Flag
        if self.boss is None and not self.flag_done:
            fx, fy = self.flag_pos
            flag_r = pygame.Rect(fx + 8, fy, 40, 120)
            if pr.colliderect(flag_r):
                self.flag_done = True
                self.score    += SCORE_FLAG * self.level
                self._advance_level()

    def _update_boss(self):
        p = self.player
        boss = self.boss

        boss.update(p.x + p.W / 2, p.y + p.H / 2)

        pr = p.rect()

        # Player vs boss body
        if boss.alive and p.invincible <= 0 and pr.colliderect(boss.rect()):
            if p.vy > 0 and pr.colliderect(boss.top_rect()):
                # Stomp
                boss.take_stomp()
                p.bounce()
                if not boss.alive:
                    self.score += SCORE_BOSS
                    self._advance_level()
                    return
            else:
                p.take_hit()
                self.lives -= 1
                if self.lives <= 0:
                    self.state = self.GAMEOVER
                return

        # Player vs projectiles
        if p.invincible <= 0:
            for proj in boss.projectiles:
                if proj.alive and pr.colliderect(proj.rect()):
                    proj.alive = False
                    p.take_hit()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = self.GAMEOVER
                    return

    def _advance_level(self):
        if self.level >= MAX_LEVEL:
            self.state = self.WIN
        else:
            self.level += 1
            # Small delay then load next level
            self.state       = self.DEAD
            self._dead_timer = 40

    # Draw
    def draw(self):
        cloud_tuples = [(c[0], c[1]) for c in self.clouds]
        draw_background(self.screen, cloud_tuples, SCREEN_W, SCREEN_H)

        if self.state in (self.PLAYING, self.DEAD):
            self._draw_world()
            self._draw_hud()

        elif self.state == self.MENU:
            self._draw_world_static()
            self._draw_menu()

        elif self.state == self.GAMEOVER:
            self._draw_world_static()
            self._draw_overlay("GAME OVER",
                               f"Score: {self.score}",
                               "PRESS ENTER TO RETRY")

        elif self.state == self.WIN:
            self._draw_world_static()
            self._draw_overlay("YOU WIN!!!!",
                               f"Final Score: {self.score}",
                               "PRESS ENTER TO PLAY AGAIN")

    def _draw_world(self):
        # Platforms (skip ground – already in background)
        for plat in self.platforms[1:]:
            draw_platform(self.screen, plat['x'], plat['y'], plat['w'])

        # Coins
        for c in self.coins:
            if not c['collected']:
                draw_coin(self.screen, int(c['x']), int(c['y']), self.frame)

        # Flag
        if self.boss is None and not self.flag_done:
            draw_flag(self.screen, self.flag_pos[0], self.flag_pos[1])

        # Enemies
        for e in self.enemies:
            e.draw(self.screen, self.frame)

        # Boss
        if self.boss is not None:
            self.boss.draw(self.screen, self.frame)

        # Player
        if self.player:
            self.player.draw(self.screen, self.frame)

    def _draw_world_static(self):
        """Draw world without a live player (for menu / overlay screens)."""
        if self.platforms:
            for plat in self.platforms[1:]:
                draw_platform(self.screen, plat['x'], plat['y'], plat['w'])
            for c in self.coins:
                if not c['collected']:
                    draw_coin(self.screen, int(c['x']), int(c['y']), self.frame)
            if self.boss is None and not self.flag_done and self.flag_pos:
                draw_flag(self.screen, self.flag_pos[0], self.flag_pos[1])
            for e in self.enemies:
                e.draw(self.screen, self.frame)
            if self.boss is not None:
                self.boss.draw(self.screen, self.frame)

    def _draw_hud(self):
        hud_surf = pygame.Surface((SCREEN_W, 30), pygame.SRCALPHA)
        hud_surf.fill(HUD_BG)
        self.screen.blit(hud_surf, (0, 0))

        score_txt = self.font_hud.render(f"SCORE: {self.score}", True, HUD_TEXT)
        level_name = LEVEL_NAMES.get(self.level, str(self.level))
        level_txt = self.font_hud.render(f"LVL {self.level}: {level_name}", True, HUD_TEXT)
        lives_txt = self.font_hud.render(f"HP x{self.lives}",       True, (255, 100, 100))

        self.screen.blit(score_txt, (10, 7))
        self.screen.blit(level_txt, (SCREEN_W // 2 - level_txt.get_width() // 2, 7))
        self.screen.blit(lives_txt, (SCREEN_W - lives_txt.get_width() - 10, 7))

    def _draw_overlay(self, title: str, subtitle: str, prompt: str):
        # Semi-transparent panel
        panel = pygame.Surface((420, 200), pygame.SRCALPHA)
        panel.fill((10, 5, 30, 230))
        px = SCREEN_W // 2 - 210
        py = SCREEN_H // 2 - 100
        self.screen.blit(panel, (px, py))
        pygame.draw.rect(self.screen, (155, 89, 182), (px, py, 420, 200), 3, border_radius=10)

        t = self.font_title.render(title,    True, (224, 86, 253))
        s = self.font_body.render(subtitle,  True, (200, 200, 200))
        b = self.font_btn.render(prompt,     True, (255, 255, 255))

        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, py + 28))
        self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, py + 90))
        self.screen.blit(b, (SCREEN_W // 2 - b.get_width() // 2, py + 140))

    def _draw_menu(self):
        panel = pygame.Surface((480, 260), pygame.SRCALPHA)
        panel.fill((10, 5, 30, 220))
        px = SCREEN_W // 2 - 240
        py = SCREEN_H // 2 - 130
        self.screen.blit(panel, (px, py))
        pygame.draw.rect(self.screen, (155, 89, 182), (px, py, 480, 260), 3, border_radius=12)

        title = self.font_title.render("PIXEL RUN", True, (224, 86, 253))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, py + 24))

        lines = [
            "Jump on enemies to defeat them!",
            "Easy -> Medium -> Hard -> Boss Fight",
            "Double-jump supported!",
        ]
        for i, line in enumerate(lines):
            t = self.font_body.render(line, True, (200, 200, 200))
            self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, py + 90 + i * 28))

        btn = self.font_btn.render("PRESS ENTER TO START", True, (255, 255, 255))
        self.screen.blit(btn, (SCREEN_W // 2 - btn.get_width() // 2, py + 208))

        # Controls hint at bottom of screen
        ctrl = self.font_hud.render(
            "← → / WASD : Move     SPACE / ↑ / W : Jump     ESC : Quit",
            True, (150, 150, 150)
        )
        self.screen.blit(ctrl, (SCREEN_W // 2 - ctrl.get_width() // 2, SCREEN_H - 22))
