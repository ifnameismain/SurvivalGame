import random
from math import atan2, degrees, pi, sin, cos
import pygame as pg


class BaseEnemy:
    def __init__(self, x, y, radius, health, dmg, speed, color):
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.radius = radius
        self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)
        self.rotation = 0
        self.previous_pos = pg.Vector2(x, y)
        self.vel = pg.Vector2(x, y)
        self.speed = speed
        self.timer = 0
        self.max_time = 15
        self.torch = False
        self.health = health
        self.max_health = health
        self.health_percentage = 1
        self.dmg = dmg
        self.type = "base"
        self.exp = 6

    def calculate_dmg(self, dmg):
        self.health -= dmg
        if self.health < 0:
            self.health = 0
            self.health_percentage = 0
        else:
            self.health_percentage = self.health/self.max_health

    def converge(self, other):
        if other.radius > self.radius:
            self.radius = other.radius + self.radius / 3
        else:
            self.radius += other.radius / 3
        self.health += other.health
        self.max_health += other.max_health
        self.health_percentage = self.health / self.max_health
        self.exp += other.exp

    def update(self, player_pos):
        rise = player_pos.y - self.pos.y
        run = player_pos.x - self.pos.x
        if run != 0:
            m = abs(rise/run)
        else:
            m = 1000
        self.previous_pos.update(self.pos.x, self.pos.y)
        if self.pos.x > player_pos.x:
            self.pos.x -= self.speed / (m + 1)
        else:
            self.pos.x += self.speed / (m + 1)
        if self.pos.y > player_pos.y:
            self.pos.y -= self.speed * m / (m + 1)
        else:
            self.pos.y += self.speed * m / (m + 1)
        self.rect.update(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        if self.health_percentage == 1:
            pg.draw.circle(win, self.color, (x, y), self.radius)
        elif self.health_percentage > 0.75:
            pg.draw.circle(win, self.color, (x, y), self.radius, draw_top_left=True,
                           draw_bottom_right=True, draw_bottom_left=True)
        elif self.health_percentage > 0.5:
            pg.draw.circle(win, self.color, (x, y), self.radius, draw_top_left=True, draw_bottom_left=True)
        else:
            pg.draw.circle(win, self.color, (x, y), self.radius, draw_top_left=True)
        pg.draw.circle(win, (255, 255, 255), (x, y), self.radius, width=1)


class Dasher(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, 4, 30, 10, 0.5, (38, 242, 143))
        self.dashing = False
        self.dash_calculated = False
        self.dash_speed = 5
        self.cooldown = False
        self.cooldown_timer = 20
        self.dash_pos = pg.Vector2(x, y)
        self.dash_distance = 50
        self.m = 0
        self.type = "dasher"
        self.max_distance = 0
        self.line = [(0, 0), (0, 0)]
        self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)

    def update(self, player_pos):
        if self.cooldown:
            self.cooldown_timer -= 1
            if self.cooldown_timer == 0:
                self.cooldown = False
                self.cooldown_timer = 20
        elif not self.dashing:
            if random.uniform(0, 1) < 0.05:
                if self.pos.distance_to(player_pos) < self.dash_distance:
                    self.dashing = True
                    self.dash(player_pos)
            else:
                super().update(player_pos)
            self.rect.update(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        else:
            self.dash(player_pos)
            self.rect.update(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    def dash(self, player_pos):
        self.previous_pos.update(self.pos.x, self.pos.y)
        if self.max_distance < self.dash_distance:
            self.dash_pos.update(player_pos.x, player_pos.y)
            if self.pos.distance_to(player_pos) < self.max_distance:
                self.line = [(self.pos.x, self.pos.y), (player_pos.x, player_pos.y)]
            else:
                dx = player_pos.x - self.pos.x
                dy = player_pos.y - self.pos.y
                rads = atan2(dy, dx)
                rads %= 2 * pi
                x = self.pos.x + cos(rads)*self.max_distance
                y = self.pos.y + sin(rads) * self.max_distance
                self.line = [(self.pos.x, self.pos.y), (x,y)]
            self.max_distance += 1
        else:
            if not self.dash_calculated:
                rise = self.dash_pos.y - self.pos.y
                run = self.dash_pos.x - self.pos.x
                if run != 0:
                    m = abs(rise / run)
                else:
                    m = 1000
                self.m = m
                if self.pos.x > player_pos.x:
                    self.dash_pos.x -= 2*self.dash_speed / (m + 1)
                else:
                    self.dash_pos.x += 2*self.dash_speed / (m + 1)
                if self.pos.y > player_pos.y:
                    self.dash_pos.y -= 2*self.dash_speed * m / (m + 1)
                else:
                    self.dash_pos.y += 2*self.dash_speed * m / (m + 1)
                self.dash_calculated = True
            if self.pos.x > self.dash_pos.x:
                self.pos.x -= self.dash_speed / (self.m + 1)
            else:
                self.pos.x += self.dash_speed / (self.m + 1)
            if self.pos.y > self.dash_pos.y:
                self.pos.y -= self.dash_speed * self.m / (self.m + 1)
            else:
                self.pos.y += self.dash_speed * self.m / (self.m + 1)
            if self.pos.distance_to(self.dash_pos) < 1.5 * self.dash_speed:
                self.dashing = False
                self.dash_calculated = False
                self.cooldown = True
                self.max_distance = 0

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        pg.draw.circle(win, self.color, (x, y), self.radius)
        pg.draw.circle(win, (255, 255, 255), (x, y), self.radius, width=1)
        if self.dashing and self.max_distance < 30:
            pg.draw.line(win, (242, 242, 38), camera.object_pos(*self.line[0]), camera.object_pos(*self.line[1]))
