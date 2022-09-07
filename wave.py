import config
import random
import pygame as pg
from enemy import BaseEnemy


class Wave:
    def __init__(self):
        self.num = 1
        self.wave_time = config.WAVE_TIME
        self.enemies = []
        self.spawn_rate = 0.001 * self.num + 0.01
        self.player_pos = pg.Vector2(0, 0)

    def new_wave(self):
        self.num += 1
        self.spawn_rate += 0.001

    def converge(self):
        for e in self.enemies.copy():
            for ee in self.enemies.copy():
                if e.type == ee.type:
                    if e != ee:
                        if e.pos.distance_to(ee.pos) < e.radius:
                            e.converge(ee)
                            self.enemies.remove(ee)

    def spawn(self):
        if random.uniform(0, 1) < self.spawn_rate:
            self.enemies.append(BaseEnemy(self.player_pos.x + random.randint(0, config.UNSCALED_SIZE[0]),
                                          self.player_pos.y + random.choice([-config.UNSCALED_SIZE[1] // 2 - 10,
                                                                             config.UNSCALED_SIZE[1] // 2 + 10]),
                                          10, 50, 10, 1, (210, 105, 30)))

    def update(self, player_pos):
        self.spawn()
        self.player_pos.update(player_pos.x, player_pos.y)