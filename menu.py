from config import *
from pg_funcs import create_card, get_mouse, centred_text
from icons import GrowingIcon, OptionIcon, ColorIcon


class Menu:
    def __init__(self, x, y, width, height, color):
        self.x, self.y, self.width, self.height, self.color = x, y, width, height, color
        self.base_card = create_card(width, height, 10, color)
        self.base_card.set_alpha(180)
        self.blank_card = create_card(width, height, 10, color)
        self.blank_card.set_colorkey(color)
        self.card = self.blank_card.copy()
        self.offset = 0
        self.multiplier = 32
        self.max_y = self.height
        self.scroller = Scroller(14, self.height-20, self.height)
        self.config_items = Config.get_items()
        self.text_objects = {k: centred_text(k, Config.FONTS['header'], (0, 0), (255, 255, 255), True)
                             for k in self.config_items.keys()}
        self.bounding_box = create_card(self.width - 40, 50, 5)
        self.option_icons = {k: [self.new_option(k, op) for op in self.config_items[k].keys()]
                             for k in self.config_items.keys()}

    def new_option(self, header, option):
        match Config.get_all_options(header, option):
            case [*options]:
                return OptionIcon(self.width//2, 50, Config.COLORS['background'],
                                  centred_text(Config.get_option(header, option), Config.FONTS['type'],
                                               (0, 0), (255, 255, 255), 0),
                                  [centred_text(o, Config.FONTS['type'],
                                               (0, 0), (255, 255, 255), 0) for o in options])
            case s:
                return ColorIcon(self.width//2, 50, Config.COLORS['background'],
                                 centred_text(s, Config.FONTS['type'],
                                              (0, 0), (255, 255, 255), 0), (Config.COLORS['slow']))

    def check_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = get_mouse()
            found = False
            for section_list in self.option_icons.values():
                if found:
                    break
                for icon in section_list:
                    if icon.rect.collidepoint(mx, my):
                        found = True
                        break

    def set_scroller_offset(self, y):
        mx, my = get_mouse()
        if self.x < mx < self.x + self.width and self.y < my < self.y + self.height:
            self.offset += self.multiplier * y
            if self.offset < 0:
                self.offset = 0
            elif self.offset > self.max_y:
                self.offset = self.max_y
            self.scroller.set_y(self.offset)

    def draw(self, win):
        self.card = self.blank_card.copy()
        win.blit(self.base_card, (self.x, self.y))
        win.blit(self.scroller.surface, (self.x+self.width-24, self.y + 10))
        o = 5 - self.offset
        for k, (h, off) in self.text_objects.items():
            self.card.blit(h, (5 + (self.width-40)//2 + off[0], o + 30 + off[1]))
            o += 65
            for kk, icons in self.option_icons.items():
                if k == kk:
                    for icon in icons:
                        surf, offset = icon.image
                        self.card.blit(surf, (3 * (self.width-40)//4 + offset[0], o + 25 + offset[1]))
                        o += 55
        win.blit(self.card, (self.x, self.y))


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
