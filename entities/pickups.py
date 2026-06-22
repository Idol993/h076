import math
import random
import pygame
from data.config import (
    XP_CRYSTAL_VALUE, XP_CRYSTAL_SIZE, XP_CRYSTAL_DROP_CHANCE,
    WEAPON_CRATE_DROP_CHANCE, SCREEN_HEIGHT, SCREEN_WIDTH,
)

_CRATE_FONT = None


def _get_crate_font():
    global _CRATE_FONT
    if _CRATE_FONT is None:
        _CRATE_FONT = pygame.font.Font(None, 18)
    return _CRATE_FONT


class XPCrystal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = XP_CRYSTAL_VALUE
        self.size = XP_CRYSTAL_SIZE
        self.alive = True
        self.lifetime = 8.0
        self.vy = 30.0
        self.vx = random.uniform(-20, 20)
        self.pulse = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.pulse += dt * 5
        if self.lifetime <= 0 or self.y > SCREEN_HEIGHT + 20:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        pulse_scale = 1.0 + 0.2 * math.sin(self.pulse)
        s = max(1, int(self.size * pulse_scale))
        alpha = 255 if self.lifetime > 2 else int(255 * self.lifetime / 2.0)
        color = (50, 200, 255)
        ix, iy = int(self.x), int(self.y)
        if alpha >= 200:
            pygame.draw.circle(surface, color, (ix, iy), s)
            pygame.draw.circle(surface, (200, 240, 255), (ix, iy), max(1, s - 2))
        else:
            crystal_surf = pygame.Surface((s * 2 + 4, s * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(crystal_surf, (*color, alpha), (s + 2, s + 2), s)
            surface.blit(crystal_surf, (ix - s - 2, iy - s - 2))


class WeaponCrate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 10
        self.alive = True
        self.lifetime = 10.0
        self.vy = 25.0
        self.vx = random.uniform(-15, 15)
        self.rotation = 0.0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.rotation += 120 * dt
        if self.lifetime <= 0 or self.y > SCREEN_HEIGHT + 20:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ix, iy = int(self.x), int(self.y)
        s = self.size
        alpha = 255 if self.lifetime > 2 else int(255 * self.lifetime / 2.0)

        if alpha >= 200:
            points = [
                (ix, iy - s),
                (ix + s, iy),
                (ix, iy + s),
                (ix - s, iy),
            ]
            pygame.draw.polygon(surface, (255, 200, 50), points)
            pygame.draw.polygon(surface, (255, 255, 150), points, 2)
            font = _get_crate_font()
            txt = font.render("W", True, (100, 50, 0))
            surface.blit(txt, (ix - txt.get_width() // 2, iy - txt.get_height() // 2))
        else:
            crate_surf = pygame.Surface((s * 2 + 4, s * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(crate_surf, (255, 200, 50, alpha), (s + 2, s + 2), s)
            surface.blit(crate_surf, (ix - s - 2, iy - s - 2))


def spawn_drops(x, y):
    drops = []
    if random.random() < XP_CRYSTAL_DROP_CHANCE:
        drops.append(XPCrystal(x, y))
    if random.random() < WEAPON_CRATE_DROP_CHANCE:
        drops.append(WeaponCrate(x, y))
    return drops
