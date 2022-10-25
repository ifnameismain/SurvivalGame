import random
from pg_funcs import *
from attacks import *
from status_icons import *


class UpgradeCard:
    width, height = 180, 320
    card = create_card(width, height, 10, color=(150, 150, 150))
    pg.draw.rect(card, Config.BACKGROUND, (width//3, 160-(width//2 - width//3), width//3, width//3))
    pg.draw.rect(card, (255, 255, 255), (width//3, 160-(width//2 - width//3), width//3, width//3), 1)

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type = random.choice([key for key in Config.UPGRADES.keys()])
        self.corner_radius = 6
        self.info_key = random.choice([key for key in Config.UPGRADES[self.type].keys()])
        self.info = Config.UPGRADES[self.type][self.info_key]
        if self.type == "attacks":
            if self.info['class'] == "Bullet":
                self.image, self.image_pos = ALL_ATTACKS[self.info['class']](
                    0, 0, pg.Vector2(1, 1), dmg=None, **self.info['inits']).get_image()
            else:
                self.image, self.image_pos = ALL_ATTACKS[self.info['class']](
                    0, 0, 0, 0, pg.Vector2(1, 1), dmg={}, **self.info['inits'], bomb_type=self.info_key).get_image()
            self.image_pos = (self.x + self.image_pos[0] + self.width//2, self.y + 160 + self.image_pos[1])

        self.name, self.name_pos = centred_text(self.info_key, Config.FONTS['name'], (self.x + self.width//2, self.y + 50),
                                                (255, 248, 220))
        self.typ, self.typ_pos = centred_text(self.info['type'], Config.FONTS['type'],
                                              (self.x + self.width // 2, self.y + 90),
                                              (205, 92, 92))
        if self.type == "attacks":
            self.dmg, self.dmg_pos = centred_text(f"{self.info['dmg']} / {self.info['cd']}s", Config.FONTS['name'],
                                                  (self.x + self.width // 2, self.y + 250),
                                                  (205, 92, 92))
            if "status" in self.info:
                self.status, self.status_pos = centred_text(f"+ {self.info['status']}", Config.FONTS['type'],
                                                  (self.x + self.width // 2, self.y + 290),
                                                  self.info['inits']['color'])
        elif self.type == "player":
            self.dmg, self.dmg_pos = centred_text(f"+ {self.info['amount']}", Config.FONTS['name'],
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


class HUD:
    def __init__(self):
        self.hp_bar = StatusBar(100, 500, 200, 20, (255, 0, 0))
        self.exp_bar = StatusBar(100, 540, 200, 20, (255, 239, 213))
        self.circle = StatusCircle(360, 500, 10, (175, 238, 238))
        self.wave = 1
        self.wave_text = centred_text("Wave: 1",  Config.FONTS['type'], (1100, 30), pg.Color('WHITE'))
        self.attacks = {}
        self.indicators = {}
        self.update_card = False
        self.indicator_card = create_card(64*len(self.indicators), 64, 16, color=Config.COLORS['light gray'])

    def update(self, hp, level, dash, wave, attacks: dict):
        self.hp_bar.update(hp)
        self.exp_bar.update(level)
        self.circle.update(dash)
        if self.wave != wave:
            self.wave = wave
            self.wave_text = left_text(f"Wave: {wave}", Config.FONTS['type'], (1100, 30), pg.Color('WHITE'))
        for attack, info in attacks.items():
            if attack not in self.attacks:
                self.update_card = True
                if info['class'] == "Bullet":
                    cast = ALL_ATTACKS[info['class']](
                        0, 0, pg.Vector2(1, 1), dmg=None, **info['inits']).get_image()
                else:
                    cast = ALL_ATTACKS[info['class']](
                        0, 0, 0, 0, pg.Vector2(1, 1), dmg={}, **info['inits'], bomb_type=attack).get_image()
                self.indicators[attack] = AttackIndicator(*cast)
                self.attacks[attack] = info
            else:
                self.indicators[attack].update(info['timer'] / info['cd'])
        if self.update_card:
            self.indicator_card = create_card(64*len(self.indicators), 64, 16, color=Config.COLORS['light gray'])

    def draw(self, win):
        self.hp_bar.draw(win)
        self.circle.draw(win)
        self.exp_bar.draw(win)
        win.blit(*self.wave_text)
        offset = - 64 * (len(self.indicators) - 1) / 2
        win.blit(self.indicator_card, (600 + offset - 32, 620 - 32))
        for indicator in self.indicators.values():
            win.blit(indicator.surface, (600 + offset - indicator.width//2, 620 - indicator.height//2))
            offset += 64


class AttackIndicator:
    def __init__(self, icon, offset):
        self.outline = Config.COLORS['outline']
        self.icon = icon
        self.offset = offset
        self.background = (0, 0, 0)
        self.percentage = 0
        self.last_percentage = 1
        self.width, self.height = (c+2 for c in icon.get_size())
        self.surface = pg.Surface((self.width, self.height))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def update(self, percentage):
        self.percentage = percentage
        if self.percentage != self.last_percentage:
            self.last_percentage = percentage
            self.create_surface()

    def create_surface(self):
        self.surface.fill((0, 0, 0))
        # draw icon
        self.surface.blit(self.icon, (self.width//2 + self.offset[0], self.height//2 + self.offset[1] + self.height * (1 - self.percentage)),
                          (0, self.height * (1 - self.percentage), self.width, self.height * self.percentage))
