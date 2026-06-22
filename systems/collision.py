import math
from entities.pickups import spawn_drops


def circle_circle(x1, y1, r1, x2, y2, r2):
    dx = x2 - x1
    dy = y2 - y1
    dist_sq = dx * dx + dy * dy
    rad_sum = r1 + r2
    return dist_sq < rad_sum * rad_sum


def check_collisions(player, enemies, bullet_pool, particles, score_counter):
    pickups = []

    for b in bullet_pool.alive_player_bullets():
        if not b.alive:
            continue
        for e in enemies:
            if not e.alive:
                continue
            if circle_circle(b.x, b.y, b.radius, e.x, e.y, e.size):
                b.alive = False
                killed = e.take_damage(b.damage)
                if killed:
                    score_counter[0] += e.score
                    pickups.extend(spawn_drops(e.x, e.y))
                    particles.spawn(e.x, e.y, e.size)
                break

    for b in bullet_pool.alive_enemy_bullets():
        if not b.alive or not player.alive:
            continue
        if circle_circle(b.x, b.y, b.radius, player.x, player.y, player.size):
            b.alive = False
            player.take_damage(1)
            particles.spawn(b.x, b.y, 5)

    for e in enemies:
        if not e.alive or not player.alive:
            continue
        if circle_circle(e.x, e.y, e.size, player.x, player.y, player.size):
            player.take_damage(1)
            e.take_damage(3)
            if not e.alive:
                score_counter[0] += e.score
                pickups.extend(spawn_drops(e.x, e.y))
                particles.spawn(e.x, e.y, e.size)

    return pickups


def check_pickup_collisions(player, pickups):
    collected = []
    for p in pickups:
        if not p.alive:
            continue
        r = p.size + player.size
        if circle_circle(p.x, p.y, p.size, player.x, player.y, player.size):
            p.alive = False
            collected.append(p)
    return collected
