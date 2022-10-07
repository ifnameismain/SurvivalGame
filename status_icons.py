from config import *


class StatusBar:
    def __init__(self, x, y, length, width, color):
        self.width = width
        self.length = length
        self.outline = Config.COLORS['outline']
        self.background = (0, 0, 0)
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.percentage = 0
        self.last_percentage = 0
        self.min_percentage = width / (length + 2 * width)
        self.surface = pg.Surface((self.length + self.width, self.width))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def update(self, percentage):
        self.percentage = percentage
        if self.last_percentage != percentage:
            self.last_percentage = percentage
            self.create_surface()

    def create_surface(self):
        self.surface.fill((0, 0, 0))
        pg.draw.circle(self.surface, self.outline, (self.width // 2, self.width // 2), self.width // 2, 1)
        pg.draw.circle(self.surface, self.outline, (self.width // 2 + self.length, self.width // 2), self.width // 2, 1)
        pg.draw.rect(self.surface, (0, 0, 0), (self.width // 2, 0, self.length, self.width))
        pg.draw.line(self.surface, self.outline, (self.width // 2, 0),
                     (self.width // 2 + self.length, 0))
        pg.draw.line(self.surface, self.outline, (self.width // 2, self.width - 1),
                     (self.width // 2 + self.length, self.width - 1))

        # percentage
        if self.percentage == 0:
            pass
        elif 0 < self.percentage < self.min_percentage:
            pg.draw.circle(self.surface, self.color, (self.width // 2, self.width // 2), -1 + self.width // 2)
        elif self.percentage > 1 - self.min_percentage:
            pg.draw.circle(self.surface, self.color, (self.width // 2, self.width // 2), -1 + self.width // 2)
            pg.draw.circle(self.surface, self.color, (self.width // 2 + self.length, self.width // 2),
                           -1 + self.width // 2)
            pg.draw.rect(self.surface, self.color, (self.width // 2, 1, self.length, self.width - 2))
        else:
            pg.draw.circle(self.surface, self.color, (self.width // 2, self.width // 2), -1 + self.width // 2)
            multiplier = (1 + self.min_percentage) / (1 - self.min_percentage) * self.percentage - self.min_percentage
            pg.draw.rect(self.surface, self.color, (self.width // 2, 1, self.length * multiplier, self.width - 2))
        self.surface.set_colorkey((0, 0, 0))

    def draw(self, win):
        win.blit(self.surface, self.pos)


class StatusCircle:
    def __init__(self, x, y, radius, color):
        self.radius = radius
        self.outline = (255, 255, 255)
        self.background = (0, 0, 0)
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.percentage = 0

    def update(self, percentage):
        self.percentage = percentage

    def draw(self, win):
        surf = pg.Surface((2 * self.radius, 2 * self.radius))
        # percentage
        if self.percentage == 1:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius)
        elif self.percentage > 0.75:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius,
                           draw_top_right=True, draw_bottom_right=True, draw_bottom_left=True)
        elif self.percentage > 0.5:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius,
                           draw_top_right=True, draw_bottom_right=True)
        elif self.percentage > 0.25:
            pg.draw.circle(surf, self.color, (self.radius, self.radius), self.radius,
                           draw_top_right=True)
        # outline
        pg.draw.circle(surf, self.outline, (self.radius, self.radius), self.radius, 1)
        surf.set_colorkey(self.background)
        win.blit(surf, self.pos)


class StatusSquare:
    def __init__(self, x, y, width, color, image):
        self.width = width
        self.image = image
        self.outline = Config.COLORS['outline']
        self.background = (0, 0, 0)
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.percentage = 1
        self.last_percentage = 1
        self.surface = pg.Surface((self.width, self.width))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()

    def update(self, percentage, color=None):
        if color is not None:
            self.color = color
        self.percentage = percentage
        if self.percentage != self.last_percentage:
            self.last_percentage = percentage
            self.create_surface()

    def create_surface(self):
        self.surface.fill((0, 0, 0))
        pg.draw.rect(self.surface, self.outline, (0, self.width * (1 - self.percentage),
                     self.width, self.width * self.percentage))
        # outline
        pg.draw.rect(self.surface, self.outline, (0, 0, self.width, self.width), 1)

    def draw(self, win):
        win.blit(self.surface, self.pos)