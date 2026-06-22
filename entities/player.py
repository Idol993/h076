import math
import pygame
from data.config import (
    PLAYER_BASE_SPEED, PLAYER_BASE_HP, PLAYER_BASE_FIRE_RATE,
    PLAYER_SHIP_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
    WEAPON_SINGLE, WEAPON_HOMING, XP_PER_LEVEL, CYAN, WHITE, HUD_HEIGHT,
)


class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2.0
        self.y = SCREEN_HEIGHT - 100.0
        self.speed = PLAYER_BASE_SPEED
        self.max_hp = PLAYER_BASE_HP
        self.hp = self.max_hp
        self.fire_rate = PLAYER_BASE_FIRE_RATE
        self.fire_cooldown = 0.0
        self.weapon_type = WEAPON_SINGLE
        self.level = 1
        self.xp = 0
        self.xp_to_next = XP_PER_LEVEL
        self.size = PLAYER_SHIP_SIZE
        self.alive = True
        self.invincible_timer = 0.0
        self.angle = -math.pi / 2

    def reset(self):
        self.x = SCREEN_WIDTH / 2.0
        self.y = SCREEN_HEIGHT - 100.0
        self.speed = PLAYER_BASE_SPEED
        self.max_hp = PLAYER_BASE_HP
        self.hp = self.max_hp
        self.fire_rate = PLAYER_BASE_FIRE_RATE
        self.fire_cooldown = 0.0
        self.weapon_type = WEAPON_SINGLE
        self.level = 1
        self.xp = 0
        self.xp_to_next = XP_PER_LEVEL
        self.alive = True
        self.invincible_timer = 0.0

    def update(self, dt, keys, mouse_pos, mouse_pressed, bullet_pool, enemies):
        if not self.alive:
            return

        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1.0

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt

        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(HUD_HEIGHT + self.size, min(SCREEN_HEIGHT - self.size, self.y))

        self.angle = math.atan2(mouse_pos[1] - self.y, mouse_pos[0] - self.x)

        self.fire_cooldown -= dt
        if mouse_pressed[0] and self.fire_cooldown <= 0:
            bx = self.x + math.cos(self.angle) * self.size
            by = self.y + math.sin(self.angle) * self.size
            bullet_pool.spawn_player_bullets(bx, by, self.angle, self.weapon_type, enemies)
            self.fire_cooldown = self.fire_rate

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

    def take_damage(self, amount):
        if self.invincible_timer > 0:
            return False
        self.hp -= amount
        self.invincible_timer = 1.0
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True

    def add_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.max_hp += 1
            self.hp = min(self.hp + 1, self.max_hp)
            self.speed *= 1.05
            self.fire_rate = max(0.05, self.fire_rate - 0.05)
            self.xp_to_next = int(XP_PER_LEVEL * (1.2 ** (self.level - 1)))
            leveled = True
        return leveled

    def upgrade_weapon(self):
        self.weapon_type = min(self.weapon_type + 1, 3)

    def draw(self, surface):
        if not self.alive:
            return
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            return

        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        s = self.size
        nose = (self.x + cos_a * s, self.y + sin_a * s)
        left = (self.x + math.cos(self.angle + 2.5) * s * 0.7,
                self.y + math.sin(self.angle + 2.5) * s * 0.7)
        right = (self.x + math.cos(self.angle - 2.5) * s * 0.7,
                 self.y + math.sin(self.angle - 2.5) * s * 0.7)
        back = (self.x - cos_a * s * 0.3, self.y - sin_a * s * 0.3)

        pygame.draw.polygon(surface, CYAN, [nose, left, back, right])
        pygame.draw.polygon(surface, WHITE, [nose, left, back, right], 1)

        engine_x = self.x - cos_a * s * 0.5
        engine_y = self.y - sin_a * s * 0.5
        flame_len = s * 0.4 + s * 0.2 * (math.sin(pygame.time.get_ticks() * 0.02) * 0.5 + 0.5)
        flame_tip = (engine_x - cos_a * flame_len, engine_y - sin_a * flame_len)
        pygame.draw.line(surface, (255, 150, 50),
                         (int(engine_x), int(engine_y)),
                         (int(flame_tip[0]), int(flame_tip[1])), 3)
