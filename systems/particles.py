import random
import math
from data.config import PARTICLE_COUNT, PARTICLE_LIFETIME, RED, ORANGE, YELLOW, WHITE


class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size']

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.life = 0.0
        self.max_life = 0.0
        self.color = (255, 255, 255)
        self.size = 2

    def spawn(self, x, y, intensity=1.0):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(40, 200) * intensity
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.max_life = PARTICLE_LIFETIME * random.uniform(0.5, 1.5)
        self.life = self.max_life
        self.size = random.randint(1, 3)
        r = random.random()
        if r < 0.3:
            self.color = YELLOW
        elif r < 0.6:
            self.color = ORANGE
        elif r < 0.85:
            self.color = RED
        else:
            self.color = WHITE

    @property
    def alive(self):
        return self.life > 0

    def update(self, dt):
        if self.life <= 0:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.98
        self.vy *= 0.98
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha_ratio = self.life / self.max_life
        size = max(1, int(self.size * alpha_ratio))
        ix, iy = int(self.x), int(self.y)
        if alpha_ratio > 0.5:
            pygame = __import__('pygame')
            pygame.draw.circle(surface, self.color, (ix, iy), size)
        else:
            faded = tuple(int(c * alpha_ratio) for c in self.color)
            pygame = __import__('pygame')
            pygame.draw.circle(surface, faded, (ix, iy), size)


class ParticleSystem:
    def __init__(self, pool_size=300):
        self.particles = [Particle() for _ in range(pool_size)]
        self.index = 0

    def spawn(self, x, y, intensity=1.0):
        count = int(PARTICLE_COUNT * intensity)
        spawned = 0
        for _ in range(count * 3):
            if spawned >= count:
                break
            p = self.particles[self.index]
            self.index = (self.index + 1) % len(self.particles)
            if not p.alive:
                p.spawn(x, y, intensity)
                spawned += 1
        while spawned < count:
            p = Particle()
            p.spawn(x, y, intensity)
            self.particles.append(p)
            spawned += 1

    def update(self, dt):
        for p in self.particles:
            if p.alive:
                p.update(dt)

    def draw(self, surface):
        for p in self.particles:
            if p.alive:
                p.draw(surface)

    def clear(self):
        for p in self.particles:
            p.life = 0
