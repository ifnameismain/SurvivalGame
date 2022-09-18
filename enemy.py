import random
from math import atan2, pi, sin, cos, sqrt
import config
from pg_funcs import *


class BaseEnemy:
    def __init__(self, x, y, radius, hp, dmg, speed, color):
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.radius = radius
        self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)
        self.rotation = 0
        self.previous_pos = pg.Vector2(x, y)
        self.vel = pg.Vector2(x, y)
        self.stats = {"max hp": hp, "hp": hp, "dmg": dmg, "hp percentage": 1, "base speed": speed, "speed": speed}
        self.status = config.BASE_STATUS.copy()
        self.timer = 0
        self.max_time = 15
        self.num_converge = 0
        self.dmg = dmg
        self.status_tick_timers = config.BASE_STATUS.copy()
        self.status_tick_rate = config.FRAME_RATE//2
        self.type = "base"
        self.exp = 15
        self.drawn_quadrants = 4
        self.drawable = False
        self.surface = pg.Surface((2 * self.radius, 2 * self.radius))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def get_notification(self):
        match len([0 for x in self.status.values() if x != 0]):
            case 0:
                return []
            case 1:
                return [centred_text(val, config.FONTS['dmg notification'], (self.pos.x + offset, self.pos.y), config.COLORS[key])
                        for (key, val), offset in zip(self.status.items(), [0]) if val != 0]
            case 2:
                return [centred_text(val, config.FONTS['dmg notification'], (self.pos.x + offset, self.pos.y),
                                     config.COLORS[key])
                        for (key, val), offset in zip(self.status.items(), [-10, 10]) if val != 0]
            case 3:
                return [centred_text(val, config.FONTS['dmg notification'], (self.pos.x + offset, self.pos.y),
                                     config.COLORS[key])
                        for (key, val), offset in zip(self.status.items(), [-20, 0, 20]) if val != 0]
            case 4:
                return [centred_text(val, config.FONTS['dmg notification'], (self.pos.x + offset, self.pos.y),
                                     config.COLORS[key])
                        for (key, val), offset in zip(self.status.items(), [-10]) if val != 0]
            case 5:
                return [centred_text(val, config.FONTS['dmg notification'], (self.pos.x + offset, self.pos.y),
                                     config.COLORS[key])
                        for (key, val), offset in zip(self.status.items(), [0]) if val != 0]

    def add_dmg(self, dmg: dict):
        for key, val in dmg.items():
            if "chance" not in key:
                self.status[key] += val

    def inflict_status(self, key, val):
        if key == "slow":
            self.stats['speed'] = self.stats['base speed'] - 0.03 * val
        else:
            self.stats['hp'] -= val * 3

    def calculate_health(self):
        if self.stats['hp'] < 0:
            self.stats['hp'] = 0
            self.stats['hp percentage'] = 0
        else:
            self.stats['hp percentage'] = self.stats['hp']/self.stats['max hp']
        return int(self.stats['hp percentage']/0.01)

    def calculate_status(self):
        prev_hp = self.stats['hp']
        for key, val in self.status.items():
            if val != 0:
                if key == "normal":
                    self.stats['hp'] -= val
                    self.status[key] = 0
                elif self.status_tick_timers[key] == self.status_tick_rate:
                    self.status_tick_timers[key] = 0
                    self.inflict_status(key, val)
                    self.status[key] -= 1
                else:
                    self.status_tick_timers[key] += 1
        if prev_hp != self.stats['hp']:
            if self.calculate_health() != self.drawn_quadrants:
                self.create_surface()

    def converge(self, other):
        if other.radius > self.radius:
            self.radius = other.radius + sqrt(self.radius) / 3
        else:
            self.radius += sqrt(other.radius) / 3
        self.stats['hp'] += other.stats['hp']
        self.stats['max hp'] += other.stats['max hp']
        self.stats['hp percentage'] = self.stats['hp'] / self.stats['max hp']
        self.exp += other.exp
        self.num_converge += other.num_converge + 1
        self.create_surface(new_radius=True)

    def update(self, player_pos):
        if self.pos.x + self.radius > player_pos.x + config.WIDTH // 2 or self.pos.x - self.radius < player_pos.x - config.WIDTH // 2:
            self.drawable = False
        elif self.pos.y + self.radius > player_pos.y + config.HEIGHT // 2 or self.pos.y - self.radius < player_pos.y - config.HEIGHT // 2:
            self.drawable = False
        else:
            self.drawable = False
        rise = player_pos.y - self.pos.y
        run = player_pos.x - self.pos.x
        if run != 0:
            m = abs(rise/run)
        else:
            m = 1000
        self.previous_pos.update(self.pos.x, self.pos.y)
        if self.pos.x > player_pos.x:
            self.pos.x -= self.stats['speed'] / (m + 1)
        else:
            self.pos.x += self.stats['speed'] / (m + 1)
        if self.pos.y > player_pos.y:
            self.pos.y -= self.stats['speed'] * m / (m + 1)
        else:
            self.pos.y += self.stats['speed'] * m / (m + 1)
        self.rect.update(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)
        self.calculate_status()

    def create_surface(self, new_radius=False):
        if new_radius:
            self.surface = pg.Surface((2 * self.radius,  2 * self.radius))
            self.surface.set_colorkey((0, 0, 0))
        self.surface.fill((0, 0, 0))
        surf_2 = pg.Surface((2*self.radius, 2*self.radius))
        surf_2.fill((0, 0, 0))
        pg.draw.rect(surf_2, self.color, (0, 2*self.radius*(1-self.stats['hp percentage']), 2 * self.radius,
                                          2*self.radius*self.stats['hp percentage']))

        pg.draw.circle(self.surface, (255, 255, 255), (self.radius, self.radius), self.radius)
        self.surface.blit(surf_2, (0, 0), special_flags=pg.BLEND_RGB_MIN)
        pg.draw.circle(self.surface, (255, 255, 255), (self.radius, self.radius), self.radius, width=1)
        if self.num_converge != 0:
            text, pos = centred_text(str(self.num_converge), config.FONTS['dmg notification'], (self.radius, self.radius), (255,255,255))
            self.surface.blit(text, pos)

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        win.blit(self.surface, (x - self.radius, y - self.radius))


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
        self.dash_vel = pg.Vector2(0, 0)
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
                self.line = [(self.pos.x, self.pos.y), (x, y)]
            self.max_distance += 1
        else:
            if not self.dash_calculated:
                rise = self.dash_pos.y - self.pos.y
                run = self.dash_pos.x - self.pos.x
                if run != 0:
                    m = abs(rise / run)
                else:
                    m = 1000
                self.dash_vel.update(2*self.dash_speed / (m + 1), 2*self.dash_speed * m / (m + 1))
                self.dash_calculated = True
            if self.pos.x > self.dash_pos.x:
                self.pos.x -= self.dash_vel.x
            else:
                self.pos.x += self.dash_vel.x
            if self.pos.y > self.dash_pos.y:
                self.pos.y -= self.dash_vel.y
            else:
                self.pos.y += self.dash_vel.y
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


class MageEnemy:
    def __init__(self, x, y, radius, hp, dmg, speed, color):
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.radius = radius
        self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)
        self.rotation = 0
        self.previous_pos = pg.Vector2(x, y)
        self.vel = pg.Vector2(x, y)
        self.stats = {"max hp": hp, "hp": hp, "dmg": dmg, "hp percentage": 1, "base speed": speed, "speed": speed}
        self.status = config.BASE_STATUS.copy()
        self.timer = 0
        self.max_time = 15
        self.num_converge = 0
        self.dmg = dmg
        self.kite = False
        self.status_tick_timers = config.BASE_STATUS.copy()
        self.status_tick_rate = config.FRAME_RATE//2
        self.type = "base"
        self.exp = 15
        self.drawn_quadrants = 4
        self.drawable = False
        self.surface = pg.Surface((2 * self.radius, 2 * self.radius))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def add_dmg(self, dmg: dict):
        for key, val in dmg.items():
            if "chance" not in key:
                self.status[key] += val

    def inflict_status(self, key, val):
        if key == "slow":
            self.stats['speed'] = self.stats['base speed'] - 0.03 * val
        else:
            self.stats['hp'] -= val * 3

    def calculate_health(self):
        if self.stats['hp'] < 0:
            self.stats['hp'] = 0
            self.stats['hp percentage'] = 0
        else:
            self.stats['hp percentage'] = self.stats['hp']/self.stats['max hp']
        return int(self.stats['hp percentage']/0.01)

    def calculate_status(self):
        prev_hp = self.stats['hp']
        for key, val in self.status.items():
            if val != 0:
                if key == "normal":
                    self.stats['hp'] -= val
                    self.status[key] = 0
                elif self.status_tick_timers[key] == self.status_tick_rate:
                    self.status_tick_timers[key] = 0
                    self.inflict_status(key, val)
                    self.status[key] -= 1
                else:
                    self.status_tick_timers[key] += 1
        if prev_hp != self.stats['hp']:
            if self.calculate_health() != self.drawn_quadrants:
                self.create_surface()

    def converge(self, other):
        if other.radius > self.radius:
            self.radius = other.radius + sqrt(self.radius) / 3
        else:
            self.radius += sqrt(other.radius) / 3
        self.stats['hp'] += other.stats['hp']
        self.stats['max hp'] += other.stats['max hp']
        self.stats['hp percentage'] = self.stats['hp'] / self.stats['max hp']
        self.exp += other.exp
        self.num_converge += other.num_converge + 1
        self.create_surface(new_radius=True)

    def update(self, player_pos):
        if self.pos.x + self.radius > player_pos.x + config.WIDTH // 2 or self.pos.x - self.radius < player_pos.x - config.WIDTH // 2:
            self.drawable = False
            if random.uniform(0, 1) < 0.02:
                self.kite = True
        elif self.pos.y + self.radius > player_pos.y + config.HEIGHT // 2 or self.pos.y - self.radius < player_pos.y - config.HEIGHT // 2:
            self.drawable = False
            if random.uniform(0, 1) < 0.02:
                self.kite = True
        else:
            self.drawable = False
        rise = player_pos.y - self.pos.y
        run = player_pos.x - self.pos.x
        if run != 0:
            m = abs(rise/run)
        else:
            m = 1000
        self.previous_pos.update(self.pos.x, self.pos.y)
        if self.pos.x > player_pos.x:
            self.pos.x -= self.stats['speed'] / (m + 1)
        else:
            self.pos.x += self.stats['speed'] / (m + 1)
        if self.pos.y > player_pos.y:
            self.pos.y -= self.stats['speed'] * m / (m + 1)
        else:
            self.pos.y += self.stats['speed'] * m / (m + 1)
        self.rect.update(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)
        self.calculate_status()

    def create_surface(self, new_radius=False):
        if new_radius:
            self.surface = pg.Surface((2 * self.radius,  2 * self.radius))
            self.surface.set_colorkey((0, 0, 0))
        self.surface.fill((0, 0, 0))
        surf_2 = pg.Surface((2*self.radius, 2*self.radius))
        surf_2.fill((0, 0, 0))
        pg.draw.rect(surf_2, self.color, (0, 2*self.radius*(1-self.stats['hp percentage']), 2 * self.radius,
                                          2*self.radius*self.stats['hp percentage']))

        pg.draw.circle(self.surface, (255, 255, 255), (self.radius, self.radius), self.radius)
        self.surface.blit(surf_2, (0, 0), special_flags=pg.BLEND_RGB_MIN)
        pg.draw.circle(self.surface, (255, 255, 255), (self.radius, self.radius), self.radius, width=1)
        if self.num_converge != 0:
            text, pos = centred_text(str(self.num_converge), config.FONTS['dmg notification'], (self.radius, self.radius), (255,255,255))
            self.surface.blit(text, pos)

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        win.blit(self.surface, (x - self.radius, y - self.radius))