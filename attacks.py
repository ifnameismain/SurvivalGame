import pygame as pg
import math


class Bullet:
    def __init__(self, x, y, velocity, color, size):
        self.pos = pg.Vector2(x, y)
        self.velocity = velocity
        self.color = color
        self.size = size
        self.rect = pg.Rect(x-size, y-size, 2*size, 2*size)
        self.dmg = 30

    def update(self):
        self.pos.update(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y)
        self.rect = pg.Rect(self.pos.x - self.size, self.pos.y - self.size, 2 * self.size, 2 * self.size)

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        pg.draw.circle(win, self.color, (x, y), self.size)


class Electricity:
    def __init__(self):
        pass


ALL_ATTACKS = {'Bullet': Bullet, "Electricity": Electricity}
