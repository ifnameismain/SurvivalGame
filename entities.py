import config
from math import sqrt, sin, cos, radians, atan, pi
from pg_funcs import *
from attacks import *
import json


class Player:
    def __init__(self, x, y):
        self.pos = pg.Vector2(x, y)
        self.w, self.hw = config.PLAYER_WIDTH, config.PLAYER_WIDTH//2
        self.rect = pg.Rect(self.pos.x-self.hw//2, self.pos.y-self.hw, self.w, self.w)
        self.color = (33, 217, 239)
        self.border = (255, 255, 255)
        self.rotation = 0
        self.previous_pos = pg.Vector2(x, y)
        self.vel = pg.Vector2(x, y)
        self.stats = {"hp": 100, "max hp": 100, "speed": 2, "attack speed": 1, "m-dmg": 1, "lvl": 1, "exp": 0}
        self.internals = {"dash cd": 1.5, "dash": 0.2, "dash timer": 0, "dash cd timer": 0}
        self.controls = {'left': pg.K_a, 'right': pg.K_d, 'up': pg.K_w, 'down': pg.K_s,
                         'dash': pg.K_SPACE}
        self.move_state = {control: False for control in self.controls.values()}
        self.dmg_notification = {}
        self.attacks = {}
        self.register_attack('Bullet')
        self.casts = []
        self.exp_percentage = 0
        self.surface = pg.Surface((self.w, self.w))
        self.create_surface()

    def add_exp(self, value):
        self.stats['exp'] += value
        if self.stats['exp'] >= self.stats['lvl'] * 5 + 10:
            self.stats['exp'] -= self.stats['lvl'] * 5 + 10
            self.stats['lvl'] += 1
            self.exp_percentage = self.stats['exp'] / (self.stats['lvl'] * 5 + 10)
            return True
        self.exp_percentage = self.stats['exp']/(self.stats['lvl'] * 5 + 10)
        return False

    def get_dash_status(self):
        return (self.internals['dash cd'] * config.FRAME_RATE - self.internals['dash cd timer'])/(
                self.internals['dash cd'] * config.FRAME_RATE
        )

    def handle_key_press(self, key, down):
        self.move_state[key] = down

    def revert_move(self):
        self.pos.update(self.previous_pos.x, self.previous_pos.y)

    def move(self):
        self.vel.x = 0
        self.vel.y = 0
        # Button presses
        if self.move_state[self.controls['left']]:
            self.vel.x -= self.stats['speed']
        if self.move_state[self.controls['right']]:
            self.vel.x += self.stats['speed']
        if self.move_state[self.controls['up']]:
            self.vel.y -= self.stats['speed']
        if self.move_state[self.controls['down']]:
            self.vel.y += self.stats['speed']

        if self.internals['dash cd timer'] != 0 and self.internals['dash timer'] == 0:
            self.internals['dash cd timer'] -= 1

        if self.internals['dash timer'] > 0:
            self.vel.x *= 4
            self.vel.y *= 4
            self.internals['dash timer'] -= 1

        # Character is running (LSHIFT) is pressed
        if self.move_state[self.controls['dash']] and self.internals['dash cd timer'] == 0:
            self.vel.x *= 4
            self.vel.y *= 4
            self.internals['dash cd timer'] = self.internals['dash cd'] * config.FRAME_RATE
            self.internals['dash timer'] = self.internals['dash'] * config.FRAME_RATE

        # Character is running diagonally (to keep same speed in all directions)
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel.x /= sqrt(2)
            self.vel.y /= sqrt(2)

        # Move x, y values by velocities
        self.previous_pos.update(self.pos.x, self.pos.y)

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

    def attack(self):
        base_velocity = None
        for attack_type, attack in self.attacks.items():
            if attack['timer'] == attack['cd'] * config.FRAME_RATE:
                if base_velocity is None:
                    self.calculate_angle()
                    base_velocity = pg.Vector2(cos(radians(self.rotation)), sin(radians(self.rotation)))
                velocity = pg.Vector2(base_velocity.x * attack['speed'], base_velocity.y * attack['speed'])
                self.casts.append(ALL_ATTACKS[attack['class']](self.pos.x, self.pos.y, velocity,
                                  notification=self.dmg_notification[attack_type],
                                  dmg=attack['dmg dict'], **attack['inits']))
                attack['timer'] = 0
            else:
                attack['timer'] += 1

    def update(self):
        self.move()
        self.attack()
        for attack in self.casts:
            attack.update()
        self.rect = pg.Rect(self.pos.x-self.hw//2, self.pos.y-self.hw, self.w, self.w)

    def calculate_angle(self):
        mx, my = get_mouse()
        x, y = mx - config.UNSCALED_SIZE[0]//2, my - config.UNSCALED_SIZE[1]//2
        if y < 0:
            self.rotation = 270 - (atan((x / y)) * 180 / pi)
        elif y > 0:
            self.rotation = 90 - (atan((x / y)) * 180 / pi)
        else:
            if x < 0:
                self.rotation = 180
            else:
                self.rotation = 0

    def update_attacks(self, key=None):
        if key is None:
            for attack in self.attacks.keys():
                self.attacks[attack]['dmg dict'] = {"normal": self.attacks[attack]['dmg']}
                if 'status' in self.attacks[attack].attacks():
                    self.attacks[attack]['dmg dict'][self.attacks[attack]["status"]] = 1
                    self.attacks[attack]['dmg dict'][self.attacks[attack]["status"] + " chance"] = self.attacks[attack]["chance"]
                self.dmg_notification[attack] = centred_text(str(self.attacks[attack]['dmg']),
                                                             config.FONTS['dmg notification'],
                                                             (0, 0), (255, 255, 255), return_offset=True)

        else:
            self.attacks[key]['dmg dict'] = {"normal": self.attacks[key]['dmg']}
            if 'status' in self.attacks[key].keys():
                self.attacks[key]['dmg dict'][self.attacks[key]["status"]] = 1
                self.attacks[key]['dmg dict'][self.attacks[key]["status"] + " chance"] = self.attacks[key]["chance"]
            self.dmg_notification[key] = centred_text(str(self.attacks[key]['dmg']), config.FONTS['dmg notification'],
                                                         (0, 0), (255, 255, 255), return_offset=True)

    def register_attack(self, attack):
        self.attacks[attack] = BASE_ATTACKS[attack]
        self.attacks[attack]['timer'] = 0
        self.update_attacks(attack)

    def create_surface(self):
        rect = pg.Rect(0, 0, self.w, self.w)
        pg.draw.rect(self.surface, self.color, rect)
        pg.draw.rect(self.surface, (255, 255, 255), rect, width=1)

    def draw(self, win, camera):
        x, y = camera.player_pos(self.pos.x, self.pos.y)
        win.blit(self.surface, (x - self.hw, y - self.hw))
        for attack in self.casts:
            attack.draw(win, camera)


class Crosshair:
    def __init__(self):
        self.x, self.y = 0, 0
        self.width = 2
        self.size = 8
        self.gap = 4

    def update(self):
        self.x, self.y = get_mouse()

    def draw(self, win):
        points_1 = [(x,y) for x, y in zip([self.x + o for o in [0, self.size, 0, -self.size]],
                                          [self.y + o for o in [-self.size, 0, self.size, 0]])]
        points_2 = [(x, y) for x, y in zip([self.x + o for o in [0, self.gap, 0, -self.gap]],
                                           [self.y + o for o in [-self.gap, 0, self.gap, 0]])]
        for p1, p2 in zip(points_1, points_2):
            pg.draw.line(win, (255, 255, 255), p1, p2)


class ExpPoint:
    point = pg.Surface((8, 8))
    pg.draw.circle(point, (135, 206, 250), (4, 4), 4)
    point.set_colorkey((0, 0, 0))

    def __init__(self, x, y, value):
        self.pos = pg.Vector2(x, y)
        self.value = value
        self.drawable = False
        self.rect = pg.Rect(x-4, y-4, 8, 8)

    def draw(self, win, camera):
        win.blit(ExpPoint.point, camera.object_pos(self.pos.x, self.pos.y))
