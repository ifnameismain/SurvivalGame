from config import *
import random
import pygame as pg
from enemy import NormalEnemy, KamikazeEnemy
from pg_funcs import get_sector_range


class Wave:
    def __init__(self):
        self.num = 1
        self.timer = 0
        self.wave_time = Config.WAVE_TIME
        self.enemies = {}
        self.spawn_rate = 0.001 * self.num + 0.01
        self.player_pos = pg.Vector2(0, 0)
        self.enemy_types = {"normal": NormalEnemy}
        self.enemy_rates = {"normal": 1}

    def new_wave(self):
        self.num += 1
        self.spawn_rate += 0.001
        self.timer -= self.wave_time

    def converge(self):
        for sector, enemies in self.enemies.items():
            for e in enemies:
                for sec in e.sectors:
                    for i, ee in enumerate(self.enemies.get(sec, []).copy()):
                        if e.type == ee.type:
                            if e != ee:
                                if e.pos.distance_to(ee.pos) < e.radius:
                                    e.converge(ee)
                                    self.enemies[sec].pop(i)
                                    break

    def spawn(self):
        if random.uniform(0, 1) < self.spawn_rate:
            x, y = random.choice(
                [(self.player_pos.x + random.choice([-Config.WIDTH // 2 - 10,
                                                    Config.WIDTH // 2 + 10]),
                 self.player_pos.y + random.randint(-Config.HEIGHT, Config.HEIGHT)),
                (self.player_pos.x + random.randint(-Config.WIDTH, Config.WIDTH),
                 self.player_pos.y + random.choice([-Config.HEIGHT // 2 - 10,
                                                    Config.HEIGHT // 2 + 10]))]

            )
            key = (int(x//Config.CHUNK_SIZE), int(y//Config.CHUNK_SIZE))
            if key not in self.enemies.keys():
                self.enemies[key] = []
            self.enemies[key].append(NormalEnemy(x, y, key))
        # if random.uniform(0, 1) < self.spawn_rate:
        #     self.enemies.append(KamikazeEnemy(self.player_pos.x + random.randint(0, Config.WIDTH),
        #                                     self.player_pos.y + random.choice([-Config.HEIGHT // 2 - 10,
        #                                                                        Config.HEIGHT // 2 + 10])))

    def update(self, player_pos):
        self.player_pos.update(player_pos.x, player_pos.y)
        self.spawn()
        if self.timer >= self.wave_time:
            self.new_wave()
        else:
            self.timer += Config.DT