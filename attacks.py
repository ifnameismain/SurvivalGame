import pygame as pg
import json
from math import sqrt
from config import *
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
        self.pos.update(self.pos.x + self.velocity.x//Config.GAME_SPEED, self.pos.y + self.velocity.y//Config.GAME_SPEED)
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
        self.state = 0 if self.time != 0 else 1
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
            self.other_surface.update()
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
            self.other_surface.draw(win, camera)


class Beam:
    def __init__(self, x, y, target_x, target_y, dmg, color, width):
        self.pos = pg.Vector2(x, y)
        self.target = pg.Vector2(target_x, target_y)
        self.time = 0
        self.state = 0
        self.color = color
        self.width = width
        self.hw = width // 2
        self.dmg = {key: val for key, val in dmg.items() if key != "normal"}
        self.dmg_tick = 0

    def check_collision(self, pos, radius):
        # line point collision <= radius + line width
        if pos.x != 0:
            m = abs(pos.y / pos.x)
        else:
            m = 1000
        return radius + self.width <= abs(m*pos.x + pos.y)/sqrt(pos.x**2 + pos.y**2)

    def update(self):
        match self.state:
            case 1:
                self.dmg_tick += 1
        self.time += 1
        if self.time % 60 == 0:
            self.state += 1
        if self.state == 0:
            self.pos.update(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y)
            self.time += 1
            if self.time == 60:
                self.state = 1
        elif self.state == 1:
            self.time += 1
            self.dmg_tick += 1
            if self.time == 120:
                self.state = 2
        else:
            self.time += 1
            self.dmg_tick += 1
            if self.time == 150:
                self.state = 2

    def get_dmg(self):
        if self.dmg_tick % 2 == 1:
            return self.dmg
        else:
            return {}

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        match self.state:
            case 0:
                pass
            case 1:
                pass
            case 2:
                pass


ALL_ATTACKS = {'Bullet': Bullet, "StatusBomb": StatusBomb, "Beam": Beam}