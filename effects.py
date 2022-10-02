from pg_funcs import *
from config import *
import random
from math import pi, cos, sin


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
        self.circles = []
        self.type = 0

    def get_image(self):
        return self.surface, (-self.radius, -self.radius)

    def update(self):
        self.animation_timer += 1
        if self.animation_timer % 2:
            self.radius -= 1
            self.create_surface()
            self.rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, 2 * self.radius, 2 * self.radius)

    def create_surface(self):
        self.surface = pg.Surface((2 * self.radius, 2 * self.radius))
        self.surface.set_colorkey((0, 0, 0))
        color = (c*0.5 for c in self.color)
        pg.draw.circle(self.surface, (*color, 0.3*255), (self.radius, self.radius), self.radius)
        pg.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius, 2)

    def animate_surface_2(self):
        surf = self.surface.copy()
        surf.set_alpha(255 * Config.STATUS_ALPHA*2)
        self.add_circles_2()
        for c in self.circles.copy():
            c[2] = c[2] - (4*pi/30)
            c[4] -= 1
            if c[4] == 0:
                self.circles.remove(c)
                continue
            pg.draw.circle(surf, self.color, (self.radius + c[0] * c[2]*cos(c[2]+c[3]), self.radius + c[0] * c[2]*sin(c[2] + c[3])), c[1])
        surf.set_alpha(255 * Config.STATUS_ALPHA*1.5)
        return surf

    def add_circles_2(self):
        for i in range(random.randint(0, 4)):
            a = random.randint(0, 359)
            self.circles.append([9*(self.radius/120), random.randint(2, 4), 4*pi, a, 30])

    def animate_surface(self):
        surf = self.surface.copy()
        surf.set_alpha(255 * Config.STATUS_ALPHA*2)
        self.add_circles()
        for c in self.circles.copy():
            c[0] += c[1]
            if c[0].length() < 2:
                self.circles.remove(c)
                continue
            pg.draw.circle(surf, self.color, (self.radius + c[0].x, self.radius + c[0].y), c[2])
        surf.set_alpha(255 * Config.STATUS_ALPHA*1.5)
        return surf

    def add_circles(self):
        for i in range(random.randint(0, 8)):
            a = random.randint(0, 359)
            v = get_angled_vector(a)
            self.circles.append([v*self.radius, v*-2, random.randint(2,4)])

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        if self.type != 0:
            surf = self.animate_surface()
        else:
            surf = self.animate_surface_2()
        win.blit(surf, (x - self.radius, y - self.radius))