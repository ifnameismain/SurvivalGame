from pg_funcs import *
from config import *
import random
from math import pi, cos, sin


def generate_spiral_effect(color, radius):
    surface = pg.Surface((2 * radius, 2 * radius))
    surface.set_colorkey((0, 0, 0))
    pg.draw.circle(surface, ((c * 0.5 for c in color), 0.3 * 255), (radius, radius), radius)
    pg.draw.circle(surface, color, (radius, radius), radius, 2)
    surface.set_alpha(255 * Config.STATUS_ALPHA*2)

    surf = surface.copy()
    surf.set_alpha(255 * Config.STATUS_ALPHA*2)
    circles = []
    for c in circles.copy():
        c[2] = c[2] - (4*pi/30)
        c[4] -= 1
        if c[4] == 0:
            circles.remove(c)
            continue
        pg.draw.circle(surf, color, (radius + c[0] * c[2]*cos(c[2]+c[3]), radius + c[0] * c[2]*sin(c[2] + c[3])), c[1])
    surf.set_alpha(255 * Config.STATUS_ALPHA*1.5)

    for i in range(random.randint(0, 4)):
        a = random.randint(0, 359)
        circles.append([9*(radius/120), random.randint(2, 4), 4*pi, a, 30])
    return surf


def generate_vacuum_effect(color, radius, t=60, density=8, step=1):
    surface_array = []
    circles = []
    r = radius
    for t in range(t):
        s = pg.Surface((2 * r, 2 * r))
        s.set_colorkey((0, 0, 0))
        pg.draw.circle(s, tuple(c * 0.5 for c in color), (r, r), r)
        pg.draw.circle(s, color, (r, r), r, 2)
        for i in range(random.randint(0, density)):
            a = random.randint(0, 359)
            v = get_angled_vector(a)
            circles.append([v * r, v * -2, random.randint(2, 4)])
        for c in circles.copy():
            c[0] += c[1]
            if c[0].length() < 2:
                circles.remove(c)
                continue
            pg.draw.circle(s, color, (r + c[0].x, r + c[0].y), c[2])
        surface_array.append(s)
        r = int(radius-step*t)
    return surface_array
