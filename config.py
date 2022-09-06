import pygame as pg
import pygame.freetype

pg.display.init()
pg.freetype.init()
GAME_CAPTION = "Rouge"
UNSCALED_SIZE = (1200, 680)
SCALED_SIZE = (1200, 680)
FRAME_RATE = 60
CONTROLS = {'player': {'up': pg.K_w, 'down': pg.K_s, 'left': pg.K_a, 'right': pg.K_d}}
FONTS = {"dmg": pg.freetype.SysFont("arial", 28, True),
         "name": pg.freetype.SysFont("arial", 24, True),
         "type": pg.freetype.SysFont("arial", 16, True),
         "upgrade": pg.freetype.SysFont("arial", 32, True)}
PLAYER_WIDTH = 18
BACKGROUND = (40, 38, 90)
pg.mouse.set_visible(False)
