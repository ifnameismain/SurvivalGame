from config import *
from pg_funcs import create_card


class BaseIcon:
    def __init__(self, x, y, width, height, color, rendered_text):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color = color
        self.rendered_text, self.offset = rendered_text
        self.surface = pg.Surface((self.width, self.height))
        self.surface.set_colorkey((0, 0, 0))
        self.hovered = False
        self.outline = Config.COLORS['outline']
        self.timer = 0
        self.create_surface()
        self.clicked = False

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
        pass

    def draw(self, win):
        win.blit(self.surface, (self.x - self.width//2, self.y - self.height//2))


class GrowingIcon(BaseIcon):
    def __init__(self, x, y, width, height, color, rendered_text, shown=True):
        super().__init__(x, y, width, height, color, rendered_text)
        self.shown = shown

    def update(self):
        if self.hovered:
            if self.timer < 0.2:
                self.timer += Config.DT
        else:
            if self.timer > 0:
                self.timer -= Config.DT

    def transform_surface(self):
        mul = self.timer/2
        return pg.transform.scale(self.surface, (self.width * (1 + mul), self.height * (1 + mul))),\
               (self.x - (self.width * mul)//2, self.y - (self.height * mul)//2)

    def draw(self, win):
        if self.shown:
            win.blit(*self.transform_surface())


class OptionIcon(BaseIcon):
    def __init__(self, width, height, color, rendered_text, option_text: list, option_info: tuple):
        super().__init__(0, 0, width, height, color, rendered_text)
        self.base_options = create_card(self.width, int(self.height * 4.5), 8, self.color)
        self.option_icons = [ColorIcon(width, height, color, t, (255, 160, 122), option_info) for t in option_text]
        self.option_info = option_info

    @property
    def image(self):
        if not self.clicked:
            return self.surface, (- self.width // 2, - self.height // 2)
        else:
            for count, icon in enumerate(self.option_icons):
                i, o = icon.image
                self.base_options.blit(i, (0, count * self.height))
            return self.base_options, (- self.width // 2, - self.height // 2)


class ColorIcon(BaseIcon):
    def __init__(self, width, height, color, rendered_text, alt_color, option_info: tuple, color_when_hover=False):
        super().__init__(0, 0, width, height, color, rendered_text)
        self.alt_color = alt_color
        self.swap_colors()
        self.inactive_surface = self.surface.copy()
        self.create_surface()
        self.swap_colors()
        self.option_info = option_info
        self.color_when_hover = color_when_hover

    def swap_colors(self):
        t = self.color
        self.color = self.alt_color
        self.alt_color = t

    def regenerate_surfaces(self):
        self.create_surface()
        self.inactive_surface = self.surface.copy()
        self.swap_colors()
        self.create_surface()
        self.swap_colors()

    @property
    def image(self):
        if self.clicked or (self.hovered and self.color_when_hover):
            return self.surface, (- self.width // 2, - self.height // 2)
        else:
            return self.inactive_surface, (- self.width // 2, - self.height // 2)