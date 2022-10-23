import pygame as pg
import pygame.freetype
import json
import configparser

pg.display.init()
pg.freetype.init()


class Config:
    _config = configparser.ConfigParser()
    _config.read('config.ini')
    GAME_CAPTION = _config['window']['game_caption']
    WIDTH, HEIGHT = 1200, 680
    UNSCALED_SIZE = (WIDTH, HEIGHT)
    SCALED_SIZE = tuple(int(d) for d in _config['window']['dimensions'].split(','))
    if SCALED_SIZE == (0, 0):
        SCALED_SIZE = UNSCALED_SIZE
    FRAME_RATE = int(_config['window']['frame_rate'])
    GAME_SPEED = int(_config['window']['speed']) * (60/FRAME_RATE)
    CONTROLS = {'player': {k: int(v) for k, v in _config['player'].items()}}
    FONTS = {}
    for k, v in _config['font_sizes'].items():
        FONTS[k] = pg.freetype.SysFont(_config['font']['type'], int(v), True)
    PLAYER_WIDTH = 18
    BACKGROUND = (120, 120, 120)
    ALT_BACKGROUND = (100, 100, 100)
    TILE_SIZE = 64
    WAVE_TIME = 20
    EXP_SIZE = 4
    BLIT_FPS = True
    NOTIFICATION_TIME = 30
    STATUS_ALPHA = 0.3
    FIRST_ATTACK = _config['window']['first_attack']
    BASE_STATUS = json.load(open("status.json", 'r'))
    UPGRADES = {"attacks": json.load(open("cards/attacks.json", 'r')),
                "player": json.load(open("cards/player.json", 'r'))}
               # "upgrades": json.load(open("cards/upgrades.json", 'r'))}
    COLORS = {"outline": (255, 255, 255),
              'background': (120, 120, 120),
              "light gray": (160, 160, 160),
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

    @classmethod
    def get_items(cls):
        return {k: {kk: v for kk, v in cls._config[k].items()} for k in ['window', 'player']}

    @classmethod
    def get_option(cls, heading: str, option: str):
        return cls._config[heading][option]

    @classmethod
    def set_option(cls, value: str, heading: str, option: str):
        try:
            int(cls._config[heading][option])
            try:
                int(value)
                cls._config[heading][option] = value
                return True
            except ValueError:
                print(f'Cant set {option} to {value}. Value needs to be an int')
                return False
        except ValueError:
            cls._config[heading][option] = value
            return True

    @classmethod
    def get_all_options(cls, heading: str, option: str):
        if option == 'dimensions':
            return [f"{w}, {h}" for (w, h) in pg.display.list_modes()]

        else:
            return cls._config[heading][option]
