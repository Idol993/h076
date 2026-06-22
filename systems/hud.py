import pygame
from data.config import (
    SCREEN_WIDTH, HUD_HEIGHT, WHITE, RED, GREEN, BLUE, YELLOW,
    DARK_GRAY, GRAY, CYAN, WEAPON_NAMES, WEAPON_COLORS, TOTAL_WAVES,
)


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 22)
        self.font_large = pygame.font.Font(None, 38)
        self.font_small = pygame.font.Font(None, 18)

    def draw(self, surface, player, wave_manager, remaining):
        pygame.draw.rect(surface, DARK_GRAY, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        pygame.draw.line(surface, GRAY, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 1)

        wave_text = f"WAVE {wave_manager.current_wave}/{TOTAL_WAVES}"
        self._draw_text(surface, wave_text, 10, 4, self.font, WHITE)

        enemies_text = f"Enemies: {remaining}"
        self._draw_text(surface, enemies_text, 10, 22, self.font_small, GRAY)

        weapon_name = WEAPON_NAMES[player.weapon_type]
        weapon_color = WEAPON_COLORS[player.weapon_type]
        weapon_text = f"Weapon: {weapon_name}"
        self._draw_text(surface, weapon_text, 160, 4, self.font, weapon_color)

        level_text = f"Lv.{player.level}"
        self._draw_text(surface, level_text, 160, 22, self.font_small, YELLOW)

        bar_x = 340
        bar_w = 150
        bar_h = 12

        hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 0
        pygame.draw.rect(surface, (60, 0, 0), (bar_x, 4, bar_w, bar_h))
        hp_color = GREEN if hp_ratio > 0.5 else YELLOW if hp_ratio > 0.25 else RED
        pygame.draw.rect(surface, hp_color, (bar_x, 4, int(bar_w * hp_ratio), bar_h))
        pygame.draw.rect(surface, WHITE, (bar_x, 4, bar_w, bar_h), 1)
        hp_text = f"HP {player.hp}/{player.max_hp}"
        self._draw_text(surface, hp_text, bar_x + 4, 3, self.font_small, WHITE)

        xp_ratio = player.xp / player.xp_to_next if player.xp_to_next > 0 else 0
        pygame.draw.rect(surface, (0, 0, 60), (bar_x, 22, bar_w, bar_h))
        pygame.draw.rect(surface, CYAN, (bar_x, 22, int(bar_w * xp_ratio), bar_h))
        pygame.draw.rect(surface, WHITE, (bar_x, 22, bar_w, bar_h), 1)
        xp_text = f"XP {player.xp}/{player.xp_to_next}"
        self._draw_text(surface, xp_text, bar_x + 4, 21, self.font_small, WHITE)

        if wave_manager.wave_announce_timer > 0:
            self._draw_wave_announce(surface, wave_manager.current_wave)

    def _draw_wave_announce(self, surface, wave_num):
        if wave_num in (5, 10):
            text = f"BOSS WAVE {wave_num}!"
            color = RED
        else:
            text = f"WAVE {wave_num}"
            color = YELLOW

        txt_surf = self.font_large.render(text, True, color)
        x = SCREEN_WIDTH // 2 - txt_surf.get_width() // 2
        y = 150
        bg_rect = pygame.Rect(x - 20, y - 10, txt_surf.get_width() + 40, txt_surf.get_height() + 20)
        bg = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg, bg_rect)
        surface.blit(txt_surf, (x, y))

    def draw_game_over(self, surface, kills, survival_time):
        overlay = pygame.Surface((SCREEN_WIDTH, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 50))

        self._draw_text_centered(surface, "GAME OVER", SCREEN_WIDTH // 2, 250, self.font_large, RED)
        self._draw_text_centered(surface, f"Kills: {kills}", SCREEN_WIDTH // 2, 310, self.font, WHITE)
        self._draw_text_centered(surface, f"Survival Time: {survival_time:.1f}s", SCREEN_WIDTH // 2, 340, self.font, WHITE)
        self._draw_text_centered(surface, "Press R to Restart | Press Q to Quit", SCREEN_WIDTH // 2, 400, self.font, GRAY)

    def draw_victory(self, surface, kills, survival_time):
        overlay = pygame.Surface((SCREEN_WIDTH, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 50))

        self._draw_text_centered(surface, "VICTORY!", SCREEN_WIDTH // 2, 250, self.font_large, YELLOW)
        self._draw_text_centered(surface, f"Kills: {kills}", SCREEN_WIDTH // 2, 310, self.font, WHITE)
        self._draw_text_centered(surface, f"Survival Time: {survival_time:.1f}s", SCREEN_WIDTH // 2, 340, self.font, WHITE)
        self._draw_text_centered(surface, "Press R to Restart | Press Q to Quit", SCREEN_WIDTH // 2, 400, self.font, GRAY)

    def draw_leaderboard(self, surface, entries):
        y_start = 440
        self._draw_text_centered(surface, "LEADERBOARD", SCREEN_WIDTH // 2, y_start, self.font, YELLOW)
        if not isinstance(entries, list):
            return
        valid_entries = []
        for e in entries[:5]:
            if isinstance(e, dict) and "kills" in e and "time" in e:
                valid_entries.append(e)
        for i, entry in enumerate(valid_entries):
            try:
                k = int(entry.get("kills", 0))
                t = float(entry.get("time", 0.0))
                txt = f"{i + 1}. {k} kills  {t:.1f}s"
                self._draw_text_centered(surface, txt, SCREEN_WIDTH // 2, y_start + 25 + i * 22,
                                         self.font_small, WHITE)
            except (TypeError, ValueError):
                continue

    def _draw_text(self, surface, text, x, y, font, color):
        txt = font.render(text, True, color)
        surface.blit(txt, (x, y))

    def _draw_text_centered(self, surface, text, cx, y, font, color):
        txt = font.render(text, True, color)
        surface.blit(txt, (cx - txt.get_width() // 2, y))
