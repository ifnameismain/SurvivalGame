import random
import config
from pg_funcs import *
from attacks import *


class StatusBar:
    def __init__(self, x, y, length, width, color):
        self.width = width
        self.length = length
        self.outline = (255, 255, 255)
        self.background = (0, 0, 0)
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.percentage = 0
        self.min_percentage = width/(length + 2*width)

    def update(self, percentage):
        self.percentage = percentage

    def draw(self, win):
        # outline
        surf = pg.Surface((self.length + self.width, self.width))
        pg.draw.circle(surf, self.outline, (self.width//2, self.width//2), self.width//2, 1)
        pg.draw.circle(surf, self.outline, (self.width//2 + self.length, self.width//2), self.width // 2, 1)
        pg.draw.rect(surf, self.background, (self.width//2, 0, self.length, self.width))
        pg.draw.line(surf, self.outline, (self.width//2, 0),
                     (self.width//2 + self.length, 0))
        pg.draw.line(surf, self.outline, (self.width//2, self.width - 1),
                     (self.width//2 + self.length, self.width - 1))

        # percentage
        if self.percentage == 0:
            pass
        elif 0 < self.percentage < self.min_percentage:
            pg.draw.circle(surf, self.color, (self.width//2, self.width//2), -1 + self.width // 2)
        elif self.percentage > 1 - self.min_percentage:
            pg.draw.circle(surf, self.color, (self.width//2, self.width//2), -1 + self.width // 2)
            pg.draw.circle(surf, self.color,  (self.width//2 + self.length, self.width//2), -1 + self.width // 2)
            pg.draw.rect(surf, self.color, (self.width//2, 1, self.length, self.width - 2))
        else:
            pg.draw.circle(surf, self.color, (self.width//2, self.width//2), -1 + self.width // 2)
            multiplier = (1 + self.min_percentage)/(1 - self.min_percentage) * self.percentage - self.min_percentage
            pg.draw.rect(surf, self.color, (self.width//2, 1, self.length * multiplier, self.width - 2))
        surf.set_colorkey(self.background)
        win.blit(surf, self.pos)


class StatusCircle:
    def __init__(self, x, y, radius, color):
        self.radius = radius
        self.outline = (255, 255, 255)
        self.background = (0, 0, 0)
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.percentage = 0

    def update(self, percentage):
        self.percentage = percentage

    def draw(self, win):
        surf = pg.Surface((2 * self.radius, 2 * self.radius))
        # outline
        pg.draw.circle(surf, self.outline, (self.radius, self.radius), self.radius, 1)
        # percentage
        if self.percentage == 1:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius-1)
        elif self.percentage > 0.75:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius-1,
                           draw_top_right=True, draw_bottom_right=True, draw_bottom_left=True)
        elif self.percentage > 0.5:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius-1,
                           draw_top_right=True, draw_bottom_right=True)
        elif self.percentage > 0.25:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius-1,
                           draw_top_right=True)
        surf.set_colorkey(self.background)
        win.blit(surf, self.pos)


class UpgradeCard:
    width, height = 180, 320
    card = create_card(width, height, 10)
    pg.draw.rect(card, config.BACKGROUND, (width//3, 160-(width//2 - width//3), width//3, width//3))
    pg.draw.rect(card, (255, 255, 255), (width//3, 160-(width//2 - width//3), width//3, width//3), 1)
    attack_stats = BASE_ATTACKS

    def __init__(self, x, y, json_path):
        self.x, self.y = x, y
        self.info = json.load(open(json_path, 'r'))
        self.corner_radius = 6
        self.info_key = random.choice([key for key in self.info.keys()])
        self.info = self.info[self.info_key]
        self.name, self.name_pos = centred_text(self.info_key, config.FONTS['name'], (self.x + self.width//2, self.y + 50),
                                                (255, 248, 220))
        self.typ, self.typ_pos = centred_text(self.info['type'], config.FONTS['type'],
                                              (self.x + self.width // 2, self.y + 90),
                                              (205, 92, 92))
        self.dmg, self.dmg_pos = centred_text(f"{self.info['dmg']} / {self.info['cd']}s", config.FONTS['name'],
                                              (self.x + self.width // 2, self.y + 260),
                                              (205, 92, 92))

    def draw(self, win):
        win.blit(self.card, (self.x, self.y))
        win.blit(self.name, self.name_pos)
        win.blit(self.typ, self.typ_pos)
        pg.draw.circle(win, self.attack_stats[self.info_key]['inits']['color'], (self.x + self.width//2, self.y + 160), 4)
        win.blit(self.dmg, self.dmg_pos)


class HUD:
    def __init__(self):
        self.hp_bar = StatusBar(100, 500, 200, 20, (255, 0, 0))
        self.exp_bar = StatusBar(100, 540, 200, 20, (255, 239, 213))
        self.circle = StatusCircle(360, 500, 10, (175, 238, 238))

    def update(self, hp, level, dash, wave, wave_timer, powers: list):
        self.hp_bar.update(hp)
        self.exp_bar.update(level)
        self.circle.update(dash)

    def draw(self, win):
        self.hp_bar.draw(win)
        self.circle.draw(win)
        self.exp_bar.draw(win)
