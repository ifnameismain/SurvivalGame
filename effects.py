import pygame as pg
import config


class AreaEffect:
    def __init__(self, x, y, color, radius, m_time=60):
        self.pos = pg.Vector2(x, y)
        self.color = color
        self.radius = radius
        self.rect = pg.Rect(x - radius, y - radius, 2 * radius, 2 * radius)
        self.surface = pg.Surface((2 * radius, 2 * radius))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()
        self.animation_timer = 0
        self.max_time = m_time

    def get_image(self):
        return self.surface, (-self.radius, -self.radius)

    def update(self, pos):
        if pos != self.pos:
            self.pos.update(pos.x, pos.y)
            self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, 2 * self.radius, 2 * self.radius)
        if self.animation_timer == self.max_time:
            self.animation_timer = 0
        self.animation_timer += 1

    def create_surface(self):
        color = (c*0.5 for c in self.color)
        pg.draw.circle(self.surface, (*color, 0.3*255), (self.radius, self.radius), self.radius)
        pg.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius, 2)

    def animate_surface(self):
        surf = self.surface.copy()
        surf.set_alpha(255 * config.STATUS_ALPHA)
        return surf

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        surf = self.animate_surface()
        win.blit(surf, (x - self.radius, y - self.radius))