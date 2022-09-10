import numpy as np
import random
import sys
import config
import pygame as pg


class Map:
    def __init__(self):
        self.surface = pg.Surface((config.WIDTH + 2 * config.TILE_SIZE,
                                   config.HEIGHT + 2 * config.TILE_SIZE))
        self.pos = pg.Vector2(0, 0)
        self.color = random.choice([config.BACKGROUND])
        self.alt_color = config.ALT_BACKGROUND
        self.tile_size = 64
        self.generate_background()

    def generate_background(self):
        self.surface.fill(self.color)
        addon = 0
        for x in range(0, 3 + config.WIDTH//config.TILE_SIZE):
            if addon == 0:
                addon = 1
            else:
                addon = 0
            for y in range(0, 3 + config.HEIGHT // config.TILE_SIZE, 2):
                pg.draw.rect(self.surface, self.alt_color,
                             (config.TILE_SIZE * x, config.TILE_SIZE * (y + addon), config.TILE_SIZE, config.TILE_SIZE))

    def update_background(self, player_pos):
        x = player_pos.x % (2 * config.TILE_SIZE)
        y = player_pos.y % (2 * config.TILE_SIZE)
        self.pos.update(-x,-y)

    def draw(self, win):
        win.blit(self.surface, self.pos)

