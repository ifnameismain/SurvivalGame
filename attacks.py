import pygame as pg
import json
from effects import AreaEffect


class Bullet:
    def __init__(self, x, y, velocity, color, radius, dmg):
        self.pos = pg.Vector2(x, y)
        self.velocity = velocity
        self.color = color
        self.radius = radius
        self.rect = pg.Rect(x-radius, y-radius, 2 * radius, 2 * radius)
        self.dmg = dmg
        self.surface = pg.Surface((2 * radius, 2 * radius))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def get_dmg(self):
        return self.dmg

    def get_image(self):
        return pg.transform.scale2x(self.surface), (-2*self.radius, -2*self.radius)

    def update(self):
        self.pos.update(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y)
        self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, 2 * self.radius, 2 * self.radius)

    def create_surface(self):
        pg.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius)

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        win.blit(self.surface, (x - self.radius, y - self.radius))


class StatusBomb:
    def __init__(self, x, y, target_x, target_y, velocity, dmg, color, alt_color, radius, other_radius):
        self.pos = pg.Vector2(x, y)
        self.target = pg.Vector2(target_x, target_y)
        self.velocity = velocity
        self.time = self.pos.distance_to(self.target) // self.velocity.magnitude()
        self.state = 0
        self.color = color
        self.radius = radius
        self.other_radius = other_radius
        self.hsize = radius // 2
        self.rect = pg.Rect(x - radius, y - radius, 2 * radius, 2 * radius)
        self.dmg = {key: val for key, val in dmg.items() if key != "normal"}
        self.dmg_tick = 0
        self.surface = pg.Surface((2 * radius, 2 * radius))
        self.surface.set_colorkey((0, 0, 0))
        self.other_surface = AreaEffect(self.target.x, self.target.y, alt_color, other_radius)
        self.create_surface()

    def update(self):
        if self.state == 0:
            self.pos.update(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y)
            self.time -= 1
            if self.time == 0:
                self.state = 1
                self.pos.update(self.target.x, self.target.y)
                self.rect = pg.Rect(self.pos.x - self.other_radius, self.pos.y - self.other_radius, 2 * self.other_radius,
                                    2 * self.other_radius)
            else:
                self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, 2 * self.radius,
                                    2 * self.radius)
        else:
            self.time += 1
            self.dmg_tick += 1
            if self.time == 120:
                self.state = 2

    def get_dmg(self):
        if self.dmg_tick % 30 == 1:
            return self.dmg
        else:
            return {}

    def get_image(self):
        return pg.transform.scale(self.other_surface.surface, (32, 32)), (-16, -16)

    def create_surface(self):
        pg.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius)

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        if self.state == 0:
            win.blit(self.surface, (x - self.radius, y - self.radius))
        else:
            win.blit(self.other_surface.surface, (x - self.other_radius, y - self.other_radius))


ALL_ATTACKS = {'Bullet': Bullet, "StatusBomb": StatusBomb}