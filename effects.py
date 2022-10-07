from pg_funcs import *
from config import *
import random
from math import pi, cos, sin, sqrt


def generate_spiral_effect(color, radius, total_time=60, density=8, step=1, circle=True):
    surface_array = []
    circles = []
    r = radius
    for t in range(total_time):
        s = pg.Surface((2 * r, 2 * r))
        s.set_colorkey((0, 0, 0))
        if circle:
            pg.draw.circle(s, tuple(c * 0.5 for c in color), (r, r), r)
            pg.draw.circle(s, color, (r, r), r, 2)
        for i in range(random.randint(0, density)):
            a = random.randint(0, 359)
            circles.append([9 * (r / 120), random.randint(2, 4), 4 * pi, a, 30])
        for c in circles.copy():
            c[2] = c[2] - (4 * pi / 30)
            c[4] -= 1
            if c[4] == 0:
                circles.remove(c)
                continue
            pg.draw.circle(s, color, (r + c[0] * c[2] * cos(c[2] + c[3]),
                                      r + c[0] * c[2] * sin(c[2] + c[3])), c[1])
        surface_array.append(s)
        r = int(radius-step*t)
    return surface_array


def generate_vacuum_effect(color, radius, total_time=60, density=8, step=1, circle=True):
    surface_array = []
    circles = []
    r = radius
    for t in range(total_time):
        s = pg.Surface((2 * r, 2 * r))
        s.set_colorkey((0, 0, 0))
        if circle:
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


def shattering_circle(color, radius, total_time=60, step: int = 5, vel=1):
    surface_array = []
    obs = []
    for i in range(-radius, radius, step):
        for j in (range(-radius, radius, step)):
            poly = False
            found = False
            rect = [i, j, step, step]
            corners = [[i, j], [i + rect[2], j], [i + rect[2], j + rect[3]], [i, j + rect[3]]]
            velocity = pg.Vector2(vel * i / radius + random.uniform(-0.5, 0.5),
                                  vel * j / radius + random.uniform(-0.5, 0.5))
            rotation = random.uniform(-1, 1)
            for c in corners:
                if sqrt(c[0]**2 + c[1]**2) > radius:
                    poly = True
                else:
                    found = True
            if found:
                obs.append({'rect': rect, 'vel': velocity, 'rot': rotation, 'poly': poly})
    for t in range(total_time):
        s = pg.Surface((4*radius, 4*radius))
        s.set_colorkey((0, 0, 0))
        for o in obs:
            m = pg.Surface((step, step))
            m.set_colorkey((0, 0, 0))
            m.set_alpha(255 * (total_time - t) // total_time)
            o["rect"][0] += o['vel'].x
            o["rect"][1] += o['vel'].y
            o['vel'].x, o['vel'].y = o['vel'].x * 0.95, o['vel'].y * 0.95
            if o['poly']:
                pg.draw.rect(m, (255,255,255), (0, 0, step, step))
            else:
                pg.draw.rect(m, tuple(c * 0.7 for c in color), (0, 0, step, step))
            s.blit(pg.transform.rotate(m, t*o['rot']), [2*radius + x for x in o['rect'][:2]])
        surface_array.append(s)
    return surface_array


def shattered_image(image, total_time=60, step: int = 5, vel=2):
    surface_array = []
    obs = []
    width, height = image.get_size()
    for j in range(0, height-step, step):
        for i in (range(0, width-step, step)):
            rect = [i, j, step, step]
            velocity = pg.Vector2(vel * (i - width/2) / (width/2) + random.uniform(-0.5, 0.5),
                                  vel * (j - width/2) / (width/2) + random.uniform(-0.5, 0.5))
            rotation = random.uniform(-1, 1)

            obs.append({'rect': rect, 'vel': velocity, 'rot': rotation})
    p = []
    for t in range(total_time):
        s = pg.Surface((2*width, 2*height))
        s.set_colorkey((0, 0, 0))
        for _ in range(len(obs)):
            p.append([])
        for i, o in enumerate(obs):
            p[i].append([o['vel'].x, o['vel'].y])
            m = image.subsurface(o['rect'])
            m.set_colorkey((0, 0, 0))
            m.set_alpha(255 * (total_time - t) // total_time)
            pp = [o['rect'][0], o['rect'][1]]
            for pv in p[i]:
               pp = [pp[0] + pv[0], pp[1] + pv[1]]
            s.blit(pg.transform.rotate(m, t*o['rot']), [width/2 + x for x in pp])
            o['vel'].x, o['vel'].y = o['vel'].x * 0.95, o['vel'].y * 0.95
        surface_array.append(s)
    return surface_array