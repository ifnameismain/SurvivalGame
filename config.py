import pygame as pg

pg.display.init()
pg.font.init()
GAME_CAPTION = "Rouge"
UNSCALED_SIZE = (1200, 680)
SCALED_SIZE = (1200, 680)
FRAME_RATE = 60
CONTROLS = {'player': {'up': pg.K_w, 'down': pg.K_s, 'left': pg.K_a, 'right': pg.K_d}}
FONTS = {"dmg": pg.font.SysFont("arial", 12, True),
         "name": pg.font.SysFont("arial", 11, True),
         "type": pg.font.SysFont("arial", 8, True)}
PLAYER_WIDTH = 18
BACKGROUND = (40, 38, 90)
pg.mouse.set_visible(False)
