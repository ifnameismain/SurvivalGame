import math
import pygame as pg
import sys
import numpy as np
from random import randint, choice

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
BG_COLOR = (0, 0, 0)

pg.init()

screen = pg.display.set_mode(SCREEN_SIZE)

clock = pg.time.Clock()

directions = ['left', 'right']

# test colors
BLACK = pg.Color(0, 0, 0)
WHITE = pg.Color(255, 255, 255)
RED = pg.Color(255, 0, 0)
GREEN = pg.Color(0, 255, 0)
BLUE = pg.Color(0, 0, 255)


def area_of_effect(x_pos, y_pos, top_color, base_color, max_rad, min_rad):
    circle_count = int((max_rad - min_rad))
    radius = max_rad
    color_layering = [0.25, 0.75]
    color_increment = (color_layering[1] - color_layering[0]) / circle_count
    color_percentage = color_layering[0]
    alpha_range = [20, 80]
    alpha_increment = (alpha_range[1] - alpha_range[0]) / circle_count
    alpha_level = alpha_range[0]
    for _ in range(circle_count):
        surface = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        color = base_color.lerp(top_color, color_percentage)
        pg.draw.circle(surface, (color[0], color[1], color[2], alpha_level), (radius, radius), radius)
        screen.blit(surface, (x_pos - radius, y_pos - radius))

        alpha_level += alpha_increment
        radius -= 1
        color_percentage += color_increment
    print('hi')

def angle_trunc(a):
    while a < 0:
        a += math.pi * 2
    return a


def lightning_rod(x, y, radius):
    pg.draw.circle(screen, (255, 255, 255), (x, y), radius)
    return x, y


def lightning_effect(dest_x, dest_y, start_x, start_y, severity_min, severity_max, severity_mag_min, severity_mag_max):
    # get line magnitude and line angle
    x_diff = dest_x - start_x
    y_diff = dest_y - start_y
    line_mag = np.sqrt(x_diff**2 + y_diff**2)
    line_angle = math.degrees(angle_trunc(math.atan2(y_diff, x_diff)))

    # amount of times line will zigzag
    line_breaks = randint(severity_min, severity_max)
    mag_split = line_mag / line_breaks
    new_points = []

    # finds all points needed to draw lines to and from
    for x in range(1, line_breaks):
        new_mag = mag_split * x
        new_x = start_x + new_mag * math.cos(math.radians(line_angle))
        new_y = start_y + new_mag * math.sin(math.radians(line_angle))
        # if branch will go left or right and change angle
        direction = choice(directions)
        if direction == 'left':
            if line_angle > 270:
                temp_angle = line_angle + 90 - 360
            else:
                temp_angle = line_angle + 90
        else:
            if line_angle < 90:
                temp_angle = line_angle - 90 + 360
            else:
                temp_angle = line_angle - 90

        temp_mag = randint(severity_mag_min, severity_mag_max)
        temp_x = new_x - temp_mag * math.cos(math.radians(temp_angle))
        temp_y = new_y - temp_mag * math.sin(math.radians(temp_angle))
        new_points.append((temp_x, temp_y))

    print(new_points)
    start_points = start_x, start_y
    end_points = dest_x, dest_y
    for x, y in new_points:
        pg.draw.line(screen, (0, 100, 200), start_points, (x, y), 3)
        start_points = x, y
    pg.draw.line(screen, (0, 100, 200), start_points, end_points, 3)



running = True
screen.fill(BG_COLOR)
while running:
    #screen.fill(BG_COLOR)
    rod_x, rod_y = lightning_rod(400, 100, 30)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if list(pg.mouse.get_pressed(num_buttons=3))[0]:
                mouse_x, mouse_y = pg.mouse.get_pos()
                lightning_effect(rod_x, rod_y, mouse_x, mouse_y, 4, 10, 0, 100)
            if list(pg.mouse.get_pressed(num_buttons=3))[2]:
                mouse_x, mouse_y = pg.mouse.get_pos()
                area_of_effect(mouse_x, mouse_y, BLUE, GREEN, 50, 10)


    clock.tick(FPS)
    pg.display.update()




