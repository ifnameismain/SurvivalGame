import numpy as np
import random
import sys
import config


class Map:
    def __init__(self):
        self.color = random.choice([config.BACKGROUND])

    def draw(self, win):
        win.fill(self.color)

