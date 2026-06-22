import math
import pygame
from data.config import (
    WEAPON_SINGLE, WEAPON_TRIPLE, WEAPON_LASER, WEAPON_HOMING,
    BULLET_SPEED, BULLET_BASE_DAMAGE, WEAPON_DAMAGE, WEAPON_COLORS,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)


class Bullet:
    __slots__ = ['x', 'y', 'vx', 'vy', 'damage', 'weapon_type',
                 'alive', 'radius', 'target', 'color', 'is_player']

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.damage = 1
        self.weapon_type = WEAPON_SINGLE
        self.alive = False
        self.radius = 3
        self.target = None
        self.color = (0, 255, 255)
        self.is_player = True

    def spawn(self, x, y, angle, weapon_type, is_player=True, target=None):
        self.x = x
        self.y = y
        self.weapon_type = weapon_type
        self.is_player = is_player
        self.alive = True
        self.target = target
        self.damage = WEAPON_DAMAGE[weapon_type] * (BULLET_BASE_DAMAGE if is_player else 1)
        self.color = WEAPON_COLORS[weapon_type] if is_player else (255, 80, 80)
        speed = BULLET_SPEED if is_player else 250

        if weapon_type == WEAPON_HOMING and target is not None:
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.radius = 4
        elif weapon_type == WEAPON_LASER:
            self.vx = math.cos(angle) * speed * 1.5
            self.vy = math.sin(angle) * speed * 1.5
            self.radius = 2
        else:
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.radius = 3

    def update(self, dt):
        if not self.alive:
            return

        if self.weapon_type == WEAPON_HOMING and self.is_player and self.target is not None:
            t = self.target
            if hasattr(t, 'x') and hasattr(t, 'alive') and t.alive:
                dx = t.x - self.x
                dy = t.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    desired = math.atan2(dy, dx)
                    current = math.atan2(self.vy, self.vx)
                    diff = desired - current
                    while diff > math.pi:
                        diff -= 2 * math.pi
                    while diff < -math.pi:
                        diff += 2 * math.pi
                    turn_rate = 4.0
                    current += max(-turn_rate * dt, min(turn_rate * dt, diff))
                    speed = math.hypot(self.vx, self.vy)
                    self.vx = math.cos(current) * speed
                    self.vy = math.sin(current) * speed

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < -20 or self.x > SCREEN_WIDTH + 20 or self.y < -20 or self.y > SCREEN_HEIGHT + 20:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ix, iy = int(self.x), int(self.y)
        if self.weapon_type == WEAPON_LASER:
            end_x = int(self.x - self.vx * 0.02)
            end_y = int(self.y - self.vy * 0.02)
            pygame.draw.line(surface, self.color, (ix, iy), (end_x, end_y), 2)
            pygame.draw.circle(surface, self.color, (ix, iy), self.radius)
        else:
            pygame.draw.circle(surface, self.color, (ix, iy), self.radius)
            if self.weapon_type == WEAPON_HOMING:
                pygame.draw.circle(surface, (255, 255, 255), (ix, iy), self.radius - 1)


class BulletPool:
    def __init__(self, size=500):
        self.bullets = [Bullet() for _ in range(size)]
        self.index = 0

    def get(self):
        for _ in range(len(self.bullets)):
            b = self.bullets[self.index]
            self.index = (self.index + 1) % len(self.bullets)
            if not b.alive:
                return b
        b = Bullet()
        self.bullets.append(b)
        return b

    def spawn_player_bullets(self, x, y, angle, weapon_type, targets=None):
        if weapon_type == WEAPON_SINGLE:
            b = self.get()
            b.spawn(x, y, angle, WEAPON_SINGLE, is_player=True)
        elif weapon_type == WEAPON_TRIPLE:
            for offset in [-0.15, 0, 0.15]:
                b = self.get()
                b.spawn(x, y, angle + offset, WEAPON_TRIPLE, is_player=True)
        elif weapon_type == WEAPON_LASER:
            b = self.get()
            b.spawn(x, y, angle, WEAPON_LASER, is_player=True)
        elif weapon_type == WEAPON_HOMING:
            target = None
            if targets:
                min_dist = float('inf')
                for t in targets:
                    if hasattr(t, 'alive') and t.alive:
                        d = math.hypot(t.x - x, t.y - y)
                        if d < min_dist:
                            min_dist = d
                            target = t
            b = self.get()
            b.spawn(x, y, angle, WEAPON_HOMING, is_player=True, target=target)

    def spawn_enemy_bullet(self, x, y, angle, speed=250):
        b = self.get()
        b.x = x
        b.y = y
        b.vx = math.cos(angle) * speed
        b.vy = math.sin(angle) * speed
        b.damage = 1
        b.weapon_type = WEAPON_SINGLE
        b.alive = True
        b.is_player = False
        b.radius = 3
        b.target = None
        b.color = (255, 80, 80)

    def update(self, dt):
        for b in self.bullets:
            if b.alive:
                b.update(dt)

    def draw(self, surface):
        for b in self.bullets:
            if b.alive:
                b.draw(surface)

    def alive_player_bullets(self):
        return [b for b in self.bullets if b.alive and b.is_player]

    def alive_enemy_bullets(self):
        return [b for b in self.bullets if b.alive and not b.is_player]

    def clear(self):
        for b in self.bullets:
            b.alive = False
