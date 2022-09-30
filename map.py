import random
import sys
from config import *
import pygame as pg


class Map:
    def __init__(self):
        self.surface = pg.Surface((Config.WIDTH + 2 * Config.TILE_SIZE,
                                   Config.HEIGHT + 2 * Config.TILE_SIZE))
        self.pos = pg.Vector2(0, 0)
        self.color = random.choice([Config.BACKGROUND])
        self.alt_color = Config.ALT_BACKGROUND
        self.tile_size = 64
        self.generate_background()

    def generate_background(self):
        self.surface.fill(self.color)
        addon = 0
        for x in range(0, 3 + Config.WIDTH//Config.TILE_SIZE):
            if addon == 0:
                addon = 1
            else:
                addon = 0
            for y in range(0, 3 + Config.HEIGHT // Config.TILE_SIZE, 2):
                pg.draw.rect(self.surface, self.alt_color,
                             (Config.TILE_SIZE * x, Config.TILE_SIZE * (y + addon), Config.TILE_SIZE, Config.TILE_SIZE))

    def update_background(self, player_pos):
        x = player_pos.x % (2 * Config.TILE_SIZE)
        y = player_pos.y % (2 * Config.TILE_SIZE)
        self.pos.update(-x,-y)

    def draw(self, win):
        win.blit(self.surface, self.pos)

