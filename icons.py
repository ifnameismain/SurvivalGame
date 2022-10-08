from config import *
from pg_funcs import create_card


class BaseIcon:
    def __init__(self, x, y, width, height, color, rendered_text, shown=True):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color = color
        self.rendered_text, self.offset = rendered_text
        self.surface = pg.Surface((self.width, self.height))
        self.surface.set_colorkey((0, 0, 0))
        self.hovered = False
        self.outline = Config.COLORS['outline']
        self.timer = 0
        self.shown = shown
        self.create_surface()

    def is_hovered(self, mx, my):
        if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
            self.hovered = True
        else:
            self.hovered = False
        return self.hovered

    def create_surface(self):
        self.surface = create_card(self.width, self.height, 8, self.color)
        self.surface.blit(self.rendered_text, (int(self.width/2 + self.offset[0]), int(self.height/2 + self.offset[1])))

    def update(self):
        if self.hovered:
            if self.timer < 0.2*Config.FRAME_RATE:
                self.timer += 1
        else:
            if self.timer > 0:
                self.timer -= 1

    def transform_surface(self):
        mul = self.timer/(2*Config.FRAME_RATE)
        return pg.transform.scale(self.surface, (self.width * (1 + mul), self.height * (1 + mul))),\
               (self.x - (self.width * mul)//2, self.y - (self.height * mul)//2)

    def draw(self, win):
        if self.shown:
            win.blit(*self.transform_surface())