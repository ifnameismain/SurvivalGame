import pygame as pg


class Bullet:
    def __init__(self, x, y, velocity, color, size, notification, p_mod=1, s_mod=1, p_flat=0, s_flat=0, status=None):
        self.pos = pg.Vector2(x, y)
        self.velocity = velocity
        self.color = color
        self.size = size
        self.hsize = size//2
        self.rect = pg.Rect(x-size, y-size, 2*size, 2*size)
        self.dmg = {"normal": int(30 * p_mod + p_flat)}
        if status is not None:
            self.dmg[status] = 3 * s_mod + s_flat
        self.surface = pg.Surface((size, size))
        self.surface.set_colorkey((0, 0, 0))
        self.create_surface()
        self.dmg_notification = notification

    def update(self):
        self.pos.update(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y)
        self.rect = pg.Rect(self.pos.x - self.size, self.pos.y - self.size, 2 * self.size, 2 * self.size)

    def create_surface(self):
        pg.draw.circle(self.surface, self.color, (self.hsize, self.hsize), self.size)

    def get_notification(self):
        return self.dmg_notification[0], [self.dmg_notification[1][0] + self.pos.x,
                                          self.dmg_notification[1][1] + self.pos.y]

    def draw(self, win, camera):
        x, y = camera.object_pos(self.pos.x, self.pos.y)
        win.blit(self.surface, (x-self.hsize, y-self.hsize))


class Electricity:
    def __init__(self):
        pass


ALL_ATTACKS = {'Bullet': Bullet, "Electricity": Electricity}
