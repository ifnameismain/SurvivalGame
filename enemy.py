import random
from math import atan2, pi, sin, cos, sqrt
from config import *
from pg_funcs import *
import sys
from effects import shattered_image


class BaseEnemy:
    # shattered array creation
    shattered_array = pg.Surface((20, 20))
    shattered_array.set_colorkey((0, 0, 0))
    pg.draw.circle(shattered_array, (255, 255, 255), (10, 10), 10, 1)
    shattered_array = shattered_image(shattered_array.copy(), step=3)

    def __init__(self, x, y, radius, hp, dmg, speed, color):
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.radius = radius
        self.rotation = 0
        self.previous_pos = pg.Vector2(x, y)
        self.vel = pg.Vector2(x, y)
        self.stats = {"max hp": hp, "hp": hp, "dmg": dmg, "hp percentage": 1, "base speed": speed, "speed": speed}
        self.status = Config.BASE_STATUS.copy()
        self.status_inflicted = self.status.copy()
        self.num_converge = 0
        self.dmg = dmg
        self.gradient = 0
        self.status_tick_timers = Config.BASE_STATUS.copy()
        self.status_tick_rates = {k: 1 if k != 'normal' else 0 for k in Config.BASE_STATUS.keys()}
        self.status_tick_rates['slow'] = 2
        self.type = "base"
        self.exp = 15
        self.drawn_quadrants = 10
        self.drawable = False
        self.surface = pg.Surface((2 * self.radius, 2 * self.radius))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()
        self.mask = pg.mask.from_surface(self.surface)
        self.attack_ready = True
        self.attack_timer = 0

    @property
    def death_animation(self):
        return self.shattered_array, self.pos, self.shattered_array[0].get_size()

    @property
    def notification(self):
        notification_list = []
        for key, val in self.status_inflicted.items():
            if self.status_tick_timers[key] >= self.status_tick_rates[key]:
                if key != 'slow' and val != 0:
                    notification_list.append(centred_text(self.calculate_status_dmg(key, val),
                                                          Config.FONTS['dmg_notification'], (self.pos.x, self.pos.y),
                                                          Config.COLORS[key]))
        match len(notification_list):
            case 0:
                pass
            case _:
                offset = - 20 * (len(notification_list) - 1)/2
                for i in notification_list:
                    i[1] = (i[1][0] - offset, i[1][1])
                    offset += 20
        return notification_list

    def set_inflicted(self):
        self.status_inflicted['normal'] = 0
        for key in self.status_inflicted:
            if self.status_tick_timers[key] >= self.status_tick_rates[key]:
                if self.status_inflicted[key] > 0:
                    self.status_inflicted[key] -= 1

    def add_dmg(self, dmg: dict):
        for key, val in dmg.items():
            if "chance" not in key:
                self.status[key] = val
                self.status_inflicted[key] += 1

    def inflict_status(self, key, val):
        if key == "slow":
            self.stats['speed'] = self.stats['base speed'] - 0.03 * val
        else:
            self.stats['hp'] -= self.calculate_status_dmg(key, val)

    def calculate_status_dmg(self, s, a):
        if s == 'normal':
            return round(self.status[s], 1)
        elif s == 'slow':
            return 0
        d = 3 + (self.status[s] * a - 1)
        return round(d, 1)

    def calculate_health(self):
        if self.stats['hp'] < 0:
            self.stats['hp'] = 0
            self.stats['hp percentage'] = 0
        else:
            self.stats['hp percentage'] = self.stats['hp']/self.stats['max hp']
        return int(self.stats['hp percentage']/0.01)

    def calculate_status(self):
        prev_hp = self.stats['hp']
        for key, val in self.status_inflicted.copy().items():
            if val != 0:
                if self.status_tick_timers[key] >= self.status_tick_rates[key]:
                    self.status_tick_timers[key] -= self.status_tick_rates[key]
                    self.inflict_status(key, val)
                else:
                    self.status_tick_timers[key] += Config.DT
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
        if self.pos.x + self.radius > player_pos.x + Config.WIDTH // 2 or self.pos.x - self.radius < player_pos.x - Config.WIDTH // 2:
            self.drawable = False
        elif self.pos.y + self.radius > player_pos.y + Config.HEIGHT // 2 or self.pos.y - self.radius < player_pos.y - Config.HEIGHT // 2:
            self.drawable = False
        else:
            self.drawable = True
        rise = player_pos.y - self.pos.y
        run = player_pos.x - self.pos.x
        if run != 0:
            self.gradient = abs(rise/run)
        else:
            self.gradient = 1000
        self.previous_pos.update(self.pos.x, self.pos.y)
        sx = self.stats['speed'] * Config.DT / (self.gradient + 1)
        sy = sx * self.gradient
        if self.pos.x > player_pos.x:
            self.pos.x -= sx
        else:
            self.pos.x += sx
        if self.pos.y > player_pos.y:
            self.pos.y -= sy
        else:
            self.pos.y += sy
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
            text, pos = centred_text(str(self.num_converge), Config.FONTS['dmg_notification'], (self.radius, self.radius), (255,255,255))
            self.surface.blit(text, pos)

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        win.blit(self.surface, (x - self.radius, y - self.radius))

    def able_to_dmg(self):
        if not self.attack_ready:
            self.attack_timer += Config.DT
            if self.attack_timer >= 1:
                self.attack_timer = 0
                self.attack_ready = True


class NormalEnemy(BaseEnemy):
    color = (210, 105, 30)

    def __init__(self, x, y):
        super().__init__(x, y, 10, 50, 1, 60, self.color)


class Dasher(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, 4, 30, 10, 60, (38, 242, 143))
        self.dashing = False
        self.dash_calculated = False
        self.dash_speed = 5
        self.cooldown = False
        self.cooldown_timer = 0.5
        self.dash_pos = pg.Vector2(x, y)
        self.dash_distance = 50
        self.dash_vel = pg.Vector2(0, 0)
        self.type = "dasher"
        self.max_distance = 0
        self.line = [(0, 0), (0, 0)]

    def update(self, player_pos):
        if self.cooldown:
            self.cooldown_timer -= Config.DT
            if self.cooldown_timer == 0:
                self.cooldown = False
                self.cooldown_timer = 0.5
        elif not self.dashing:
            if random.uniform(0, 1) < 0.05:
                if self.pos.distance_to(player_pos) < self.dash_distance:
                    self.dashing = True
                    self.dash(player_pos)
            else:
                super().update(player_pos)
        else:
            self.dash(player_pos)

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
                self.dash_vel.update(2*self.dash_speed * Config.DT / (m + 1), 2*self.dash_speed * m * Config.DT / (m + 1))
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


class MageEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, 4, 30, 10, 60, (38, 242, 143))
        self.type = "mage"

    def update(self, player_pos):
        super().update(player_pos)

    def draw(self, win, camera):
        super().draw(win, camera)


class KamikazeEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, 5, 10, 50, 180, random.choice([Config.BACKGROUND, Config.ALT_BACKGROUND]))
        self.type = "kamikaze"

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
        if self.stats['hp'] != self.stats['max hp']:
            pg.draw.circle(self.surface, (220, 0, 0), (self.radius, self.radius), self.radius, width=1)

    def converge(self, other):
        pass

    def update(self, player_pos):
        super().update(player_pos)





