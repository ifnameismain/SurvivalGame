from config import *
from math import atan, pi
from pg_funcs import *
from attacks import *


class Player:
    def __init__(self, x, y):
        self.pos = pg.Vector2(x, y)
        self.w, self.hw = Config.PLAYER_WIDTH, Config.PLAYER_WIDTH//2
        self.color = (33, 217, 239)
        self.border = (255, 255, 255)
        self.rotation = 0
        self.vel = pg.Vector2(x, y)
        self.stats = {"hp": 100, "max hp": 100, "speed": 120, "attack speed": 1, "flat dmg": 0,
                      "% damage": 1, "flat status": 0, "% status": 1, "lvl": 1, "exp": 0}
        self.internals = {"dash cd": 1.5, "dash": 0.15, "dash timer": 0.0, "dash cd timer": 0.0}
        self.controls = Config.CONTROLS['player']
        self.move_state = {control: False for control in self.controls.values()}
        self.dmg_notification = {}
        self.attacks = {}
        self.register_attack(Config.FIRST_ATTACK)
        self.casts = []
        self.exp_percentage = 0
        self.surface = pg.Surface((self.w, self.w))
        self.create_surface()
        self.mask = pg.mask.from_surface(self.surface)
        self.sector = [0, 0]

    @property
    def dash_status(self):
        return (self.internals['dash cd'] - self.internals['dash cd timer'])/(
                self.internals['dash cd']
        )

    def modify_stats(self, stat):
        s = Config.UPGRADES['player'][stat]
        self.stats[s['stat']] += s['amount']
        if s['stat'] == "max hp":
            self.stats["hp"] += s['amount']
        elif s['stat'] == "speed":
            pass
        else:
            self.update_attacks()

    def modify_attacks(self, stat):
        pass

    def register_upgrade(self, upgrades: list):
        for upgrade in upgrades:
            if upgrade in Config.UPGRADES['attacks'].keys():
                self.register_attack(upgrade)
            elif upgrade in Config.UPGRADES['player'].keys():
                self.modify_stats(upgrade)
            else:
                self.modify_attacks(upgrade)

    def add_exp(self, value):
        self.stats['exp'] += value
        while self.stats['exp'] >= self.stats['lvl'] * 5 + 10:
            self.stats['exp'] -= self.stats['lvl'] * 5 + 10
            self.stats['lvl'] += 1
            self.exp_percentage = self.stats['exp'] / (self.stats['lvl'] * 5 + 10)
        self.exp_percentage = self.stats['exp']/(self.stats['lvl'] * 5 + 10)

    def handle_key_press(self, key, down):
        self.move_state[key] = down

    def move(self):
        self.vel.x = 0
        self.vel.y = 0
        # Button presses
        speed = self.stats['speed'] * Config.DT
        if self.move_state[self.controls['left']]:
            self.vel.x -= speed
        if self.move_state[self.controls['right']]:
            self.vel.x += speed
        if self.move_state[self.controls['up']]:
            self.vel.y -= speed
        if self.move_state[self.controls['down']]:
            self.vel.y += speed

        if self.internals['dash cd timer'] >= 0 >= self.internals['dash timer']:
            self.internals['dash cd timer'] -= Config.DT

        if self.internals['dash timer'] > 0:
            self.vel.x *= 4
            self.vel.y *= 4
            self.internals['dash timer'] -= Config.DT

        # Character is running (LSHIFT) is pressed
        if self.move_state[self.controls['dash']] and self.internals['dash cd timer'] <= 0:
            self.vel.x *= 4
            self.vel.y *= 4
            self.internals['dash cd timer'] = self.internals['dash cd']
            self.internals['dash timer'] = self.internals['dash']

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel.x /= sqrt(2)
            self.vel.y /= sqrt(2)

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.sector[0] = int(self.pos.x//Config.CHUNK_SIZE)
        self.sector[1] = int(self.pos.y//Config.CHUNK_SIZE)

    def attack(self, camera):
        base_velocity = None
        for attack_type, attack in self.attacks.items():
            if attack['timer'] >= attack['cd']:
                if base_velocity is None:
                    self.calculate_angle()
                    base_velocity = get_angled_vector(self.rotation)
                if attack['class'] == "Bullet":
                    velocity = pg.Vector2(base_velocity.x * attack['speed'], base_velocity.y * attack['speed'])
                    self.casts.append(ALL_ATTACKS[attack['class']](self.pos.x, self.pos.y, velocity,
                                      dmg=attack['dmg dict'], **attack['inits']))
                else:
                    velocity = pg.Vector2(base_velocity.x * attack['speed'], base_velocity.y * attack['speed'])
                    self.casts.append(ALL_ATTACKS[attack['class']](self.pos.x, self.pos.y,
                                                                   *camera.player_relative(*get_mouse()), velocity,
                                                                   dmg=attack['dmg dict'], bomb_type=attack_type, **attack['inits']))
                attack['timer'] = 0
            else:
                attack['timer'] += Config.DT

    def update(self, camera):
        self.move()
        self.attack(camera)
        for attack in self.casts:
            attack.update()

    def calculate_angle(self):
        mx, my = get_mouse()
        x, y = mx - Config.WIDTH//2, my - Config.HEIGHT//2
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
                self.attacks[attack]['dmg dict'] = {"normal": (self.attacks[attack]['dmg'] +
                                                               self.stats['flat dmg']) * self.stats['% damage']}
                if 'status' in self.attacks[attack].keys():
                    status = self.attacks[attack]["status"]
                    self.attacks[attack]['dmg dict'][status] = (1 + self.stats['flat status']) * self.stats['% status']
                    self.attacks[attack]['dmg dict'][status + " chance"] = self.attacks[attack]["chance"]
        else:
            self.attacks[key]['dmg dict'] = {"normal": (self.attacks[key]['dmg'] +
                                                        self.stats['flat dmg']) * self.stats['% damage']}
            if 'status' in self.attacks[key].keys():
                status = self.attacks[key]["status"]
                self.attacks[key]['dmg dict'][status] = (1 + self.stats['flat status']) * self.stats['% status']
                self.attacks[key]['dmg dict'][status + " chance"] = self.attacks[key]["chance"]

    def register_attack(self, attack):
        self.attacks[attack] = Config.UPGRADES['attacks'][attack]
        if 'timer' not in self.attacks[attack]:
            self.attacks[attack]['timer'] = 0
        self.update_attacks(attack)

    def create_surface(self):
        rect = pg.Rect(0, 0, self.w, self.w)
        pg.draw.rect(self.surface, self.color, rect)
        pg.draw.rect(self.surface, (255, 255, 255), rect, width=1)

    def draw_casts(self, win, camera):
        for attack in self.casts:
            attack.draw(win, camera)

    def draw(self, win, camera):
        x, y = camera.player_pos(self.pos.x, self.pos.y)
        win.blit(self.surface, (x - self.hw, y - self.hw))


class Crosshair:
    def __init__(self):
        self.x, self.y = 0, 0
        self.width = 2
        self.size = 8
        self.gap = 4

    def update(self):
        self.x, self.y = get_mouse()

    def draw(self, win):
        points_1 = [(x, y) for x, y in zip([self.x + o for o in [0, self.size, 0, -self.size]],
                                          [self.y + o for o in [-self.size, 0, self.size, 0]])]
        points_2 = [(x, y) for x, y in zip([self.x + o for o in [0, self.gap, 0, -self.gap]],
                                           [self.y + o for o in [-self.gap, 0, self.gap, 0]])]
        for p1, p2 in zip(points_1, points_2):
            pg.draw.line(win, (255, 255, 255), p1, p2)


class ExpPoint:
    point = pg.Surface((2*Config.EXP_SIZE, 2*Config.EXP_SIZE))
    pg.draw.circle(point, (135, 206, 250), (Config.EXP_SIZE, Config.EXP_SIZE), Config.EXP_SIZE)
    point.set_colorkey((0, 0, 0))
    mask = pg.mask.from_surface(point)

    def __init__(self, x, y, value):
        self.pos = pg.Vector2(x, y)
        self.value = value
        self.radius = Config.EXP_SIZE
        self.drawable = False

    def draw(self, win, camera):
        win.blit(ExpPoint.point, camera.object_pos(self.pos.x - 4, self.pos.y - 4))

