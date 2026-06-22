import math
import random
import pygame
from data.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_HEIGHT,
    ASTEROID_HP, ASTEROID_SPEED, ASTEROID_SIZE, ASTEROID_SCORE,
    PATROL_HP, PATROL_SPEED, PATROL_SIZE, PATROL_FIRE_RATE,
    PATROL_BULLET_SPEED, PATROL_SCORE,
    MOTHERSHIP_HP, MOTHERSHIP_SPEED, MOTHERSHIP_SIZE,
    MOTHERSHIP_SPAWN_INTERVAL, MOTHERSHIP_SCORE,
    BOSS_HP_WAVE5, BOSS_HP_WAVE10, BOSS_SPEED, BOSS_SIZE,
    BOSS_FIRE_RATE, BOSS_BULLET_SPEED, BOSS_SHIELD_DURATION,
    BOSS_BERSERK_THRESHOLD, BOSS_SCORE,
    RED, ORANGE, PURPLE, WHITE, YELLOW, CYAN, GRAY,
)


class Asteroid:
    def __init__(self, target_x=None, target_y=None):
        self.x = random.uniform(50, SCREEN_WIDTH - 50)
        self.y = -ASTEROID_SIZE
        self.hp = ASTEROID_HP
        self.max_hp = ASTEROID_HP
        self.speed = ASTEROID_SPEED * random.uniform(0.8, 1.2)
        self.size = ASTEROID_SIZE * random.uniform(0.8, 1.2)
        self.alive = True
        self.score = ASTEROID_SCORE
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)

        tx = target_x if target_x else SCREEN_WIDTH / 2
        ty = target_y if target_y else SCREEN_HEIGHT
        angle = math.atan2(ty - self.y, tx - self.x)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

        num_verts = random.randint(6, 9)
        self.vertices = []
        for i in range(num_verts):
            a = (2 * math.pi / num_verts) * i
            r = self.size * random.uniform(0.7, 1.0)
            self.vertices.append((a, r))

    def update(self, dt, player=None, bullet_pool=None):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rot_speed * dt

        if self.y > SCREEN_HEIGHT + 50 or self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.alive = False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        cos_r = math.cos(math.radians(self.rotation))
        sin_r = math.sin(math.radians(self.rotation))
        points = []
        for a, r in self.vertices:
            px = self.x + (math.cos(a) * r * cos_r - math.sin(a) * r * sin_r)
            py = self.y + (math.cos(a) * r * sin_r + math.sin(a) * r * cos_r)
            points.append((int(px), int(py)))
        if len(points) >= 3:
            pygame.draw.polygon(surface, GRAY, points)
            pygame.draw.polygon(surface, WHITE, points, 1)


class Patrol:
    STATE_ZIG = 0
    STATE_ZAG = 1

    def __init__(self, target_x=None, target_y=None):
        self.x = random.uniform(50, SCREEN_WIDTH - 50)
        self.y = -PATROL_SIZE
        self.hp = PATROL_HP
        self.max_hp = PATROL_HP
        self.speed = PATROL_SPEED
        self.size = PATROL_SIZE
        self.alive = True
        self.score = PATROL_SCORE
        self.fire_cooldown = random.uniform(0.5, PATROL_FIRE_RATE)
        self.state = self.STATE_ZIG
        self.state_timer = random.uniform(1.0, 2.0)
        self.vx = random.choice([-1, 1]) * self.speed
        self.vy = self.speed * 0.5

    def update(self, dt, player=None, bullet_pool=None):
        self.state_timer -= dt
        if self.state_timer <= 0:
            self.state = self.STATE_ZAG if self.state == self.STATE_ZIG else self.STATE_ZIG
            self.state_timer = random.uniform(1.0, 2.0)
            self.vx = -self.vx

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < self.size:
            self.x = self.size
            self.vx = abs(self.vx)
        elif self.x > SCREEN_WIDTH - self.size:
            self.x = SCREEN_WIDTH - self.size
            self.vx = -abs(self.vx)

        if bullet_pool and player and player.alive:
            self.fire_cooldown -= dt
            if self.fire_cooldown <= 0 and self.y < SCREEN_HEIGHT * 0.7:
                angle = math.atan2(player.y - self.y, player.x - self.x)
                bullet_pool.spawn_enemy_bullet(self.x, self.y, angle, PATROL_BULLET_SPEED)
                self.fire_cooldown = PATROL_FIRE_RATE

        if self.y > SCREEN_HEIGHT + 50:
            self.alive = False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        s = self.size
        points = [
            (ix, iy - s),
            (ix + s, iy),
            (ix, iy + s // 2),
            (ix - s, iy),
        ]
        pygame.draw.polygon(surface, ORANGE, points)
        pygame.draw.polygon(surface, YELLOW, points, 1)


class Mothership:
    def __init__(self, target_x=None, target_y=None):
        self.x = random.uniform(100, SCREEN_WIDTH - 100)
        self.y = -MOTHERSHIP_SIZE
        self.hp = MOTHERSHIP_HP
        self.max_hp = MOTHERSHIP_HP
        self.speed = MOTHERSHIP_SPEED
        self.size = MOTHERSHIP_SIZE
        self.alive = True
        self.score = MOTHERSHIP_SCORE
        self.spawn_timer = MOTHERSHIP_SPAWN_INTERVAL
        self.target_y = random.uniform(80, 200)
        self.drifting = False
        self.drift_dir = random.choice([-1, 1])

    def update(self, dt, player=None, bullet_pool=None):
        if not self.drifting:
            self.y += self.speed * dt
            if self.y >= self.target_y:
                self.y = self.target_y
                self.drifting = True
        else:
            self.x += self.drift_dir * self.speed * 0.5 * dt
            if self.x < 100 or self.x > SCREEN_WIDTH - 100:
                self.drift_dir = -self.drift_dir

    def should_spawn_patrol(self, dt):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = MOTHERSHIP_SPAWN_INTERVAL
            return True
        return False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        s = self.size
        points = [
            (ix, iy - s),
            (ix + s, iy - s // 3),
            (ix + s * 2 // 3, iy + s // 2),
            (ix - s * 2 // 3, iy + s // 2),
            (ix - s, iy - s // 3),
        ]
        pygame.draw.polygon(surface, PURPLE, points)
        pygame.draw.polygon(surface, WHITE, points, 1)
        pygame.draw.circle(surface, RED, (ix, iy), s // 3)
        if self.alive and self.hp < self.max_hp:
            bar_w = s * 2
            bar_h = 4
            ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, RED, (ix - bar_w // 2, iy - s - 8, bar_w, bar_h))
            pygame.draw.rect(surface, GREEN, (ix - bar_w // 2, iy - s - 8, int(bar_w * ratio), bar_h))


class Boss:
    STATE_ENTER = 0
    STATE_NORMAL = 1
    STATE_SHIELD = 2
    STATE_BERSERK = 3

    def __init__(self, wave_number):
        self.x = SCREEN_WIDTH / 2
        self.y = -BOSS_SIZE
        self.wave = wave_number
        if wave_number >= 10:
            self.hp = BOSS_HP_WAVE10
            self.max_hp = BOSS_HP_WAVE10
        else:
            self.hp = BOSS_HP_WAVE5
            self.max_hp = BOSS_HP_WAVE5
        self.speed = BOSS_SPEED
        self.size = BOSS_SIZE
        self.alive = True
        self.score = BOSS_SCORE
        self.state = self.STATE_ENTER
        self.fire_cooldown = BOSS_FIRE_RATE
        self.shield_timer = BOSS_SHIELD_DURATION
        self.shield_active = False
        self.target_y = 120.0
        self.drift_dir = 1
        self.pattern_timer = 0.0
        self.burst_count = 0

    def update(self, dt, player=None, bullet_pool=None):
        if self.state == self.STATE_ENTER:
            self.y += self.speed * dt
            if self.y >= self.target_y:
                self.y = self.target_y
                self.state = self.STATE_NORMAL
                self.shield_timer = BOSS_SHIELD_DURATION
            return

        self.x += self.drift_dir * self.speed * dt
        if self.x < BOSS_SIZE + 20:
            self.drift_dir = 1
        elif self.x > SCREEN_WIDTH - BOSS_SIZE - 20:
            self.drift_dir = -1

        hp_ratio = self.hp / self.max_hp

        if self.state == self.STATE_NORMAL:
            if hp_ratio <= 0.6 and not self.shield_active:
                self.state = self.STATE_SHIELD
                self.shield_timer = BOSS_SHIELD_DURATION
                self.shield_active = True
            if hp_ratio <= BOSS_BERSERK_THRESHOLD:
                self.state = self.STATE_BERSERK

        elif self.state == self.STATE_SHIELD:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
                self.state = self.STATE_NORMAL
            if hp_ratio <= BOSS_BERSERK_THRESHOLD:
                self.state = self.STATE_BERSERK
                self.shield_active = False

        elif self.state == self.STATE_BERSERK:
            self.speed = BOSS_SPEED * 2

        if player and player.alive and bullet_pool:
            fire_rate = BOSS_FIRE_RATE * (0.5 if self.state == self.STATE_BERSERK else 1.0)
            self.fire_cooldown -= dt
            if self.fire_cooldown <= 0:
                self._fire_pattern(player, bullet_pool)
                self.fire_cooldown = fire_rate

    def _fire_pattern(self, player, bullet_pool):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        if self.state == self.STATE_BERSERK:
            for i in range(-2, 3):
                bullet_pool.spawn_enemy_bullet(
                    self.x, self.y + self.size, angle + i * 0.2, BOSS_BULLET_SPEED)
        else:
            bullet_pool.spawn_enemy_bullet(
                self.x, self.y + self.size, angle, BOSS_BULLET_SPEED)
            bullet_pool.spawn_enemy_bullet(
                self.x - self.size, self.y + self.size // 2, angle - 0.15, BOSS_BULLET_SPEED)
            bullet_pool.spawn_enemy_bullet(
                self.x + self.size, self.y + self.size // 2, angle + 0.15, BOSS_BULLET_SPEED)

    def take_damage(self, amount):
        if self.shield_active:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        s = self.size

        body = [
            (ix, iy - s),
            (ix + s, iy - s // 3),
            (ix + s * 3 // 4, iy + s),
            (ix - s * 3 // 4, iy + s),
            (ix - s, iy - s // 3),
        ]
        color = RED if self.state == self.STATE_BERSERK else (200, 50, 50)
        pygame.draw.polygon(surface, color, body)
        pygame.draw.polygon(surface, WHITE, body, 2)

        core_color = YELLOW if self.state != self.STATE_BERSERK else (255, 100, 0)
        pygame.draw.circle(surface, core_color, (ix, iy), s // 3)

        if self.shield_active:
            shield_alpha = int(128 + 64 * math.sin(pygame.time.get_ticks() * 0.005))
            shield_surf = pygame.Surface((s * 3, s * 3), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 150, 255, shield_alpha),
                               (s * 3 // 2, s * 3 // 2), s * 3 // 2, 3)
            surface.blit(shield_surf, (ix - s * 3 // 2, iy - s * 3 // 2))

        bar_w = s * 3
        bar_h = 6
        ratio = self.hp / self.max_hp
        bx = ix - bar_w // 2
        by = iy - s - 15
        pygame.draw.rect(surface, (60, 60, 60), (bx, by, bar_w, bar_h))
        bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
        pygame.draw.rect(surface, bar_color, (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, WHITE, (bx, by, bar_w, bar_h), 1)
