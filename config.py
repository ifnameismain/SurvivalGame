import pygame as pg
import pygame.freetype
import json

pg.display.init()
pg.freetype.init()
GAME_CAPTION = "Rouge"
WIDTH, HEIGHT = 1200, 680
UNSCALED_SIZE = (WIDTH, HEIGHT)
SCALED_SIZE = (1200, 680)
FRAME_RATE = 60
CONTROLS = {'player': {'up': pg.K_w, 'down': pg.K_s, 'left': pg.K_a, 'right': pg.K_d}}
FONTS = {"title": pg.freetype.SysFont("arial", 48, True),
         "dmg": pg.freetype.SysFont("arial", 28, True),
         "name": pg.freetype.SysFont("arial", 24, True),
         "type": pg.freetype.SysFont("arial", 16, True),
         "upgrade": pg.freetype.SysFont("arial", 32, True),
         "dmg notification": pg.freetype.SysFont("arial", 14, True)}
PLAYER_WIDTH = 18
BACKGROUND = (120, 120, 120)
ALT_BACKGROUND = (100, 100, 100)
TILE_SIZE = 64
WAVE_TIME = 90
NOTIFICATION_TIME = 30
STATUS_ALPHA = 0.3
BASE_STATUS = json.load(open("status.json", 'r'))
UPGRADES = {"attacks": json.load(open("cards/attacks.json", 'r')),
            "player": json.load(open("cards/player.json", 'r'))}
           # "upgrades": json.load(open("cards/upgrades.json", 'r'))}

pg.mouse.set_visible(False)
COLORS = {"outline": (255, 255, 255),
          'background': (120, 120, 120),
          'alt background': (100, 100, 100),
          "normal": (255, 255, 255),
          "burn": (245, 183, 177),
          "slow": (174, 214, 241),
          "poison": (171, 235, 198),
          "bleed": (210, 180, 222)}
for attack in UPGRADES['attacks'].values():
    if 'status' in attack.keys():
        attack['inits']['color'] = COLORS[attack['status']]
    else:
        attack['inits']['color'] = COLORS["normal"]
    if attack['class'] in ["StatusBomb"]:
        attack['inits']['alt_color'] = COLORS[attack['status']]
