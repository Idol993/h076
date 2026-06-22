import random
from data.config import (
    TOTAL_WAVES, WAVE_ENEMY_BASE, WAVE_ENEMY_INCREMENT,
)
from entities.enemies import Asteroid, Patrol, Mothership, Boss


class WaveManager:
    def __init__(self):
        self.current_wave = 0
        self.enemies_to_spawn = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.8
        self.wave_active = False
        self.wave_complete = False
        self.all_waves_complete = False
        self.wave_announce_timer = 0.0
        self.boss = None

    def start_next_wave(self):
        self.current_wave += 1
        if self.current_wave > TOTAL_WAVES:
            self.all_waves_complete = True
            return

        self.wave_active = True
        self.wave_complete = False
        self.wave_announce_timer = 2.5
        self.enemies_to_spawn = []
        self.spawn_timer = 0.0

        if self.current_wave in (5, 10):
            self.boss = Boss(self.current_wave)
            count = WAVE_ENEMY_BASE + (self.current_wave - 1) * WAVE_ENEMY_INCREMENT // 2
            self._fill_spawn_list(count, boss_wave=True)
            self.spawn_interval = 0.5
        else:
            count = WAVE_ENEMY_BASE + (self.current_wave - 1) * WAVE_ENEMY_INCREMENT
            self._fill_spawn_list(count)
            self.spawn_interval = max(0.3, 0.8 - self.current_wave * 0.04)

    def _fill_spawn_list(self, count, boss_wave=False):
        for _ in range(count):
            roll = random.random()
            if self.current_wave < 3:
                if roll < 0.7:
                    self.enemies_to_spawn.append('asteroid')
                else:
                    self.enemies_to_spawn.append('patrol')
            elif self.current_wave < 5:
                if roll < 0.5:
                    self.enemies_to_spawn.append('asteroid')
                else:
                    self.enemies_to_spawn.append('patrol')
            else:
                if roll < 0.3:
                    self.enemies_to_spawn.append('asteroid')
                elif roll < 0.7:
                    self.enemies_to_spawn.append('patrol')
                else:
                    self.enemies_to_spawn.append('mothership')
        random.shuffle(self.enemies_to_spawn)

    def update(self, dt, active_enemies, player):
        if self.all_waves_complete:
            return []

        if self.wave_announce_timer > 0:
            self.wave_announce_timer -= dt
            return []

        new_enemies = []

        if self.boss and self.boss.alive and self.boss.state >= Boss.STATE_NORMAL:
            if self.boss.should_spawn_patrol(dt):
                p = Patrol(player.x if player else None, player.y if player else None)
                p.x = self.boss.x + random.uniform(-30, 30)
                p.y = self.boss.y + self.boss.size
                new_enemies.append(p)

        if self.enemies_to_spawn:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                etype = self.enemies_to_spawn.pop(0)
                if etype == 'asteroid':
                    new_enemies.append(Asteroid(player.x if player else None,
                                                player.y if player else None))
                elif etype == 'patrol':
                    new_enemies.append(Patrol(player.x if player else None,
                                              player.y if player else None))
                elif etype == 'mothership':
                    new_enemies.append(Mothership(player.x if player else None,
                                                  player.y if player else None))
                self.spawn_timer = self.spawn_interval

        if self.boss and self.boss.state == Boss.STATE_ENTER:
            pass
        elif not self.enemies_to_spawn:
            boss_alive = self.boss is not None and self.boss.alive
            active_count = len(active_enemies)
            if not boss_alive and active_count == 0:
                self.wave_active = False
                self.wave_complete = True
                self.boss = None

        return new_enemies

    def get_boss(self):
        b = self.boss
        self.boss = None
        return b

    def remaining_enemies(self, active_enemies):
        return len(self.enemies_to_spawn) + len(active_enemies) + (1 if self.boss and self.boss.alive else 0)

    def reset(self):
        self.current_wave = 0
        self.enemies_to_spawn = []
        self.spawn_timer = 0.0
        self.wave_active = False
        self.wave_complete = False
        self.all_waves_complete = False
        self.wave_announce_timer = 0.0
        self.boss = None
