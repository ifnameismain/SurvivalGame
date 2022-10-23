from config import *
from pg_funcs import create_card, get_mouse, centred_text
from icons import GrowingIcon, OptionIcon


class Menu:
    def __init__(self, x, y, width, height, color):
        self.x, self.y, self.width, self.height, self.color = x, y, width, height, color
        self.card = create_card(width, height, 10, color)
        self.card.set_alpha(180)
        self.offset = 0
        self.multiplier = 32
        self.max_y = self.height
        self.scroller = Scroller(14, self.height-20, self.height)
        self.items = Config.get_items()
        self.text_objects = {k: centred_text(k, Config.FONTS['header'], (0, 0), (255, 255, 255), True) for k in self.items.keys()}
        self.bounding_box = create_card(self.width - 40, 50, 5)
        self.typable_icons = []
        self.option_icons = {k: OptionIcon((self.width-40)//2, 50, Config.COLORS['slow'],
                                           centred_text(k, Config.FONTS['type'], ((self.width-40)//4, 25), (255, 255, 255), True),
                                           [centred_text(vv, Config.FONTS['type'],
                                                         ((self.width-40)//4, 25), (255, 255, 255), True) for vv
                                            in v.values()]) for k, v in self.items.items()}

    def check_event(self, y):
        mx, my = get_mouse()
        if self.x < mx < self.x + self.width and self.y < my < self.y + self.height:
            self.offset += self.multiplier * y
            if self.offset < 0:
                self.offset = 0
            elif self.offset > self.max_y:
                self.offset = self.max_y
            self.scroller.set_y(self.offset)

    def draw(self, win):
        win.blit(self.card, (self.x, self.y))
        win.blit(self.scroller.surface, (self.x+self.width-24, self.y + 10))
        o = 5
        for k, (h, off) in self.text_objects.items():
            win.blit(h, (self.x + 5 + (self.width-40)//2 + off[0], self.y + o + 50 + off[1]))
            o += 105
            for kk, icon in self.option_icons.items():
                if k == kk:
                    surf, offset = icon.get_image()
                    win.blit(surf, (self.x + 3 * (self.width-40)//4 + offset[0], self.y + o + 25 + offset[1]))
                    o += 55


class Scroller:
    def __init__(self, width, height, max_y):
        self.width, self.height = width, height
        self.max_y = max_y
        if max_y < height:
            self.slider_enabled = False
        else:
            self.slider_enabled = True
        self.slider_height = int(self.height/(max(1, max_y/height)))
        self.base_surface = create_card(self.width, self.height, self.width//6, (0, 0, 0))
        self.slider = create_card(self.width, self.slider_height, self.width//6, (255, 255, 255))
        self.surface = None
        self.set_y()

    def set_y(self, offset=0):
        surf = self.base_surface.copy()
        surf.blit(self.slider, (0, int((self.height-self.slider_height) * offset/self.max_y)))
        self.surface = surf
