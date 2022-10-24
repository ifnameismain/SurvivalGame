from config import *
import random
import pygame as pg
from enemy import NormalEnemy, KamikazeEnemy


class Wave:
    def __init__(self):
        self.num = 1
        self.timer = 0
        self.wave_time = Config.WAVE_TIME * Config.FRAME_RATE
        self.enemies = []
        self.spawn_rate = 0.001 * self.num + 0.01
        self.player_pos = pg.Vector2(0, 0)
        self.enemy_types = {"normal": NormalEnemy}
        self.enemy_rates = {"normal": 1}

    def new_wave(self):
        self.num += 1
        self.spawn_rate += 0.001
        self.wave_time = 0

    def converge(self):
        for e in self.enemies:
            for ee in self.enemies:
                if e.type == ee.type:
                    if e != ee:
                        if e.pos.distance_to(ee.pos) < e.radius:
                            e.converge(ee)
                            self.enemies.remove(ee)
                            break

    def spawn(self):
        if random.uniform(0, 1) < self.spawn_rate:
            self.enemies.append(NormalEnemy(self.player_pos.x + random.randint(0, Config.WIDTH),
                                            self.player_pos.y + random.choice([-Config.HEIGHT // 2 - 10,
                                                                               Config.HEIGHT // 2 + 10])))
        if random.uniform(0, 1) < self.spawn_rate:
            self.enemies.append(KamikazeEnemy(self.player_pos.x + random.randint(0, Config.WIDTH),
                                            self.player_pos.y + random.choice([-Config.HEIGHT // 2 - 10,
                                                                               Config.HEIGHT // 2 + 10])))

    def update(self, player_pos):
        self.player_pos.update(player_pos.x, player_pos.y)
        self.spawn()
        if self.timer == self.wave_time:
            self.new_wave()
        else:
            self.timer += 1
