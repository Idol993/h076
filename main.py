import sys
import json
import os
import math
import random
import pygame

from data.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, GRAY, CYAN,
    HUD_HEIGHT, LEADERBOARD_FILE, LEADERBOARD_MAX_ENTRIES, TOTAL_WAVES,
)
from entities.player import Player
from entities.bullets import BulletPool
from entities.enemies import Asteroid, Patrol, Mothership, Boss
from entities.pickups import XPCrystal, WeaponCrate
from systems.wave_manager import WaveManager
from systems.collision import check_collisions, check_pickup_collisions
from systems.hud import HUD
from systems.particles import ParticleSystem


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Space Survivor - 10 Waves")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.player = Player()
        self.bullet_pool = BulletPool(500)
        self.wave_manager = WaveManager()
        self.hud = HUD()
        self.particles = ParticleSystem(500)

        self.enemies = []
        self.pickups = []
        self.score = [0]
        self.kills = 0
        self.survival_time = 0.0
        self.game_state = "menu"
        self.wave_delay = 0.0
        self.stars = self._generate_stars()

        self.leaderboard = self._load_leaderboard()

    def _generate_stars(self):
        stars = []
        for _ in range(150):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            brightness = random.randint(80, 255)
            speed = random.uniform(10, 50)
            size = random.choice([1, 1, 1, 2])
            stars.append([x, y, brightness, speed, size])
        return stars

    def _load_leaderboard(self):
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_leaderboard(self):
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump(self.leaderboard, f, indent=2)
        except IOError:
            pass

    def _add_to_leaderboard(self, kills, time_val):
        self.leaderboard.append({"kills": kills, "time": round(time_val, 1)})
        self.leaderboard.sort(key=lambda e: (-e["kills"], e["time"]))
        self.leaderboard = self.leaderboard[:LEADERBOARD_MAX_ENTRIES]
        self._save_leaderboard()

    def reset_game(self):
        self.player.reset()
        self.bullet_pool.clear()
        self.wave_manager.reset()
        self.particles.clear()
        self.enemies.clear()
        self.pickups.clear()
        self.score = [0]
        self.kills = 0
        self.survival_time = 0.0
        self.wave_delay = 2.0
        self.game_state = "playing"

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "menu":
                        if event.key == pygame.K_RETURN:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
                    elif self.game_state == "game_over" or self.game_state == "victory":
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
                    elif self.game_state == "playing":
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"

            if self.game_state == "menu":
                self._update_stars(dt)
                self._draw_menu()
            elif self.game_state == "playing":
                self._update_game(dt)
                self._draw_game()
            elif self.game_state == "game_over":
                self._draw_game()
                self.hud.draw_game_over(self.screen, self.kills, self.survival_time)
                self.hud.draw_leaderboard(self.screen, self.leaderboard)
            elif self.game_state == "victory":
                self._draw_game()
                self.hud.draw_victory(self.screen, self.kills, self.survival_time)
                self.hud.draw_leaderboard(self.screen, self.leaderboard)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _update_stars(self, dt):
        for star in self.stars:
            star[1] += star[3] * dt
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)

    def _draw_stars(self):
        for star in self.stars:
            color = (star[2], star[2], star[2])
            pygame.draw.circle(self.screen, color, (int(star[0]), int(star[1])), star[4])

    def _draw_menu(self):
        self.screen.fill(BLACK)
        self._draw_stars()
        font_title = pygame.font.Font(None, 56)
        font_sub = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)

        title = font_title.render("SPACE SURVIVOR", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

        sub = font_sub.render("Survive 10 Waves to Win!", True, WHITE)
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 270))

        controls = [
            "WASD - Move    Mouse - Aim    Left Click - Shoot",
            "Defeat enemies for XP and weapon upgrades",
            "Boss waves at 5 and 10!",
        ]
        for i, line in enumerate(controls):
            txt = font_small.render(line, True, GRAY)
            self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 330 + i * 25))

        prompt = font_sub.render("Press ENTER to Start", True, YELLOW)
        pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.003))
        prompt.set_alpha(pulse)
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 440))

        quit_txt = font_small.render("Press Q to Quit", True, GRAY)
        self.screen.blit(quit_txt, (SCREEN_WIDTH // 2 - quit_txt.get_width() // 2, 480))

        if self.leaderboard:
            self.hud.draw_leaderboard(self.screen, self.leaderboard)

    def _update_game(self, dt):
        self.survival_time += dt
        self._update_stars(dt)

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        self.player.update(dt, keys, mouse_pos, mouse_pressed, self.bullet_pool, self.enemies)

        if not self.player.alive:
            self._add_to_leaderboard(self.kills, self.survival_time)
            self.game_state = "game_over"
            return

        if self.wave_delay > 0:
            self.wave_delay -= dt
            if self.wave_delay <= 0:
                self.wave_manager.start_next_wave()
        elif self.wave_manager.all_waves_complete:
            self._add_to_leaderboard(self.kills, self.survival_time)
            self.game_state = "victory"
            return
        elif not self.wave_manager.wave_active and self.wave_manager.wave_complete:
            self.wave_delay = 2.0
            self.wave_manager.wave_complete = False

        new_enemies = self.wave_manager.update(dt, self.enemies, self.player)
        self.enemies.extend(new_enemies)

        boss = self.wave_manager.get_boss_if_not_added()
        if boss:
            self.enemies.append(boss)

        for e in self.enemies:
            e.update(dt, self.player, self.bullet_pool)

        mothership_spawns = []
        for e in self.enemies:
            if isinstance(e, Mothership) and e.alive and e.drifting:
                if e.should_spawn_patrol(dt):
                    p = Patrol(self.player.x if self.player else None,
                               self.player.y if self.player else None)
                    p.x = e.x + random.uniform(-20, 20)
                    p.y = e.y + e.size
                    mothership_spawns.append(p)
        self.enemies.extend(mothership_spawns)

        self.bullet_pool.update(dt)
        self.particles.update(dt)

        new_pickups = check_collisions(self.player, self.enemies, self.bullet_pool,
                                       self.particles, self.score)
        self.pickups.extend(new_pickups)

        for p in self.pickups:
            p.update(dt)

        collected = check_pickup_collisions(self.player, self.pickups)
        for item in collected:
            if isinstance(item, XPCrystal):
                self.player.add_xp(item.value)
            elif isinstance(item, WeaponCrate):
                self.player.upgrade_weapon()

        before = len(self.enemies)
        self.enemies = [e for e in self.enemies if e.alive]
        self.kills += before - len(self.enemies)

        self.pickups = [p for p in self.pickups if p.alive]

    def _draw_game(self):
        self.screen.fill(BLACK)
        self._draw_stars()

        for p in self.pickups:
            p.draw(self.screen)

        self.bullet_pool.draw(self.screen)

        for e in self.enemies:
            e.draw(self.screen)

        self.player.draw(self.screen)
        self.particles.draw(self.screen)

        remaining = self.wave_manager.remaining_enemies(self.enemies)
        self.hud.draw(self.screen, self.player, self.wave_manager, remaining)


if __name__ == "__main__":
    game = Game()
    game.run()
