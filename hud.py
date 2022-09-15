import random
import config
from pg_funcs import *
from attacks import *


class StatusBar:
    def __init__(self, x, y, length, width, color):
        self.width = width
        self.length = length
        self.outline = config.COLORS['outline']
        self.background = (0, 0, 0)
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.percentage = 0
        self.last_percentage = 0
        self.min_percentage = width/(length + 2*width)
        self.surface = pg.Surface((self.length + self.width, self.width))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def update(self, percentage):
        self.percentage = percentage
        if self.last_percentage != percentage:
            self.last_percentage = percentage
            self.create_surface()
        
    def create_surface(self):
        self.surface.fill((0, 0, 0))
        pg.draw.circle(self.surface, self.outline, (self.width // 2, self.width // 2), self.width // 2, 1)
        pg.draw.circle(self.surface, self.outline, (self.width // 2 + self.length, self.width // 2), self.width // 2, 1)
        pg.draw.rect(self.surface, (0, 0, 0), (self.width // 2, 0, self.length, self.width))
        pg.draw.line(self.surface, self.outline, (self.width // 2, 0),
                     (self.width // 2 + self.length, 0))
        pg.draw.line(self.surface, self.outline, (self.width // 2, self.width - 1),
                     (self.width // 2 + self.length, self.width - 1))

        # percentage
        if self.percentage == 0:
            pass
        elif 0 < self.percentage < self.min_percentage:
            pg.draw.circle(self.surface, self.color, (self.width // 2, self.width // 2), -1 + self.width // 2)
        elif self.percentage > 1 - self.min_percentage:
            pg.draw.circle(self.surface, self.color, (self.width // 2, self.width // 2), -1 + self.width // 2)
            pg.draw.circle(self.surface, self.color, (self.width // 2 + self.length, self.width // 2), -1 + self.width // 2)
            pg.draw.rect(self.surface, self.color, (self.width // 2, 1, self.length, self.width - 2))
        else:
            pg.draw.circle(self.surface, self.color, (self.width // 2, self.width // 2), -1 + self.width // 2)
            multiplier = (1 + self.min_percentage) / (1 - self.min_percentage) * self.percentage - self.min_percentage
            pg.draw.rect(self.surface, self.color, (self.width // 2, 1, self.length * multiplier, self.width - 2))
        self.surface.set_colorkey((0, 0, 0))

    def draw(self, win):
        win.blit(self.surface, self.pos)


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
        # percentage
        if self.percentage == 1:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius)
        elif self.percentage > 0.75:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius,
                           draw_top_right=True, draw_bottom_right=True, draw_bottom_left=True)
        elif self.percentage > 0.5:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius,
                           draw_top_right=True, draw_bottom_right=True)
        elif self.percentage > 0.25:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius,
                           draw_top_right=True)
        # outline
        pg.draw.circle(surf, self.outline, (self.radius, self.radius), self.radius, 1)
        surf.set_colorkey(self.background)
        win.blit(surf, self.pos)


class UpgradeCard:
    width, height = 180, 320
    card = create_card(width, height, 10, color=(150, 150, 150))
    pg.draw.rect(card, config.BACKGROUND, (width//3, 160-(width//2 - width//3), width//3, width//3))
    pg.draw.rect(card, (255, 255, 255), (width//3, 160-(width//2 - width//3), width//3, width//3), 1)

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choice([key for key in config.UPGRADES.keys()])
        self.corner_radius = 6
        self.info_key = random.choice([key for key in config.UPGRADES[self.type].keys()])
        self.info = config.UPGRADES[self.type][self.info_key]
        if self.type == "attacks":
            self.image, self.image_pos = ALL_ATTACKS[config.UPGRADES[self.type][self.info_key]['class']](
                0, 0, pg.Vector2(0, 0), notification=None, dmg=None, **self.info['inits']).get_image()
            self.image_pos = (self.x + self.image_pos[0] + self.width//2, self.y + 160 + self.image_pos[1])

        self.name, self.name_pos = centred_text(self.info_key, config.FONTS['name'], (self.x + self.width//2, self.y + 50),
                                                (255, 248, 220))
        self.typ, self.typ_pos = centred_text(self.info['type'], config.FONTS['type'],
                                              (self.x + self.width // 2, self.y + 90),
                                              (205, 92, 92))
        if self.type == "attacks":
            self.dmg, self.dmg_pos = centred_text(f"{self.info['dmg']} / {self.info['cd']}s", config.FONTS['name'],
                                                  (self.x + self.width // 2, self.y + 250),
                                                  (205, 92, 92))
            if "status" in self.info:
                self.status, self.status_pos = centred_text(f"+ {self.info['status']}", config.FONTS['type'],
                                                  (self.x + self.width // 2, self.y + 290),
                                                  self.info['inits']['color'])
        elif self.type == "player":
            self.dmg, self.dmg_pos = centred_text(f"+ {self.info['amount']}", config.FONTS['name'],
                                                  (self.x + self.width // 2, self.y + 260),
                                                  (205, 92, 92))
        else:
            pass

    def draw(self, win):
        win.blit(self.card, (self.x, self.y))
        win.blit(self.name, self.name_pos)
        win.blit(self.typ, self.typ_pos)
        if self.type == "attacks":
            win.blit(self.image, self.image_pos)
        win.blit(self.dmg, self.dmg_pos)
        if "status" in self.info:
            win.blit(self.status, self.status_pos)


class StatusSquare:
    def __init__(self, x, y, width, color, image):
        self.width = width
        self.image = image
        self.outline = (255, 255, 255)
        self.background = (0, 0, 0)
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.percentage = 1
        self.last_percentage = 1
        self.surface = pg.Surface((self.width, self.width))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def update(self, percentage, color=None):
        if color is not None:
            self.color = color
        self.percentage = percentage
        if self.percentage != self.last_percentage:
            self.last_percentage = percentage
            self.create_surface()

    def create_surface(self):
        self.surface.fill((0, 0, 0))
        pg.draw.rect(self.surface, config.COLORS['outline'], (0, self.width * (1 - self.percentage),
                                                              self.width, self.width * self.percentage))
        # outline
        pg.draw.rect(self.surface, config.COLORS['outline'], (0, 0, self.width, self.width), 1)

    def draw(self, win):
        win.blit(self.surface, self.pos)


class HUD:
    def __init__(self):
        self.hp_bar = StatusBar(100, 500, 200, 20, (255, 0, 0))
        self.exp_bar = StatusBar(100, 540, 200, 20, (255, 239, 213))
        self.circle = StatusCircle(360, 500, 10, (175, 238, 238))

    def update(self, hp, level, dash, wave, wave_timer, powers: list):
        self.hp_bar.update(hp)
        self.exp_bar.update(level)
        self.circle.update(dash)
        for power in powers:
            pass


    def draw(self, win):
        self.hp_bar.draw(win)
        self.circle.draw(win)
        self.exp_bar.draw(win)
