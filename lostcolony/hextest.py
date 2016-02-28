import sys
import os
sys.path.insert(0, '.')

import random
from math import cos, sin, radians, sqrt
from pathfinding import Grid, NoPath
from collections import deque

ON = 255, 255, 255
OFF = 255, 128, 128
PATH = 0, 255, 0
HOVER = 0, 128, 255,

size = 36.0

root3 = sqrt(3)


def draw_hex(x, y, color, size=size):
    pts = []
    s = size - 3
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = radians(angle_deg)
        pts.append((
            x + s * cos(angle_rad),
            y + s * sin(angle_rad)
        ))
    for a, b in zip(pts, pts[1:] + pts[:1]):
        screen.draw.line(a, b, color)


def cube_round(h):
    x, y, z = h
    rx = round(x)
    ry = round(y)
    rz = round(z)

    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry

    return rx, ry, rz


def cube_to_hex(h):
    x, _, z = h
    return x, z + (x + (int(x) % 2)) // 2


def hex_to_cube(h):
    c, r = h

    x = c
    z = r - (c + (int(c) % 2)) // 2
    return (
        x,
        -x - z,
        z
    )


def hex_round(h):
    return cube_to_hex(cube_round(hex_to_cube(h)))


def pixel_to_hex(x, y):
    q = x * 2/3 / size
    r = (-x / 3 + root3 / 3 * y) / size
    return cube_to_hex(cube_round((q, -q - r, r)))


g = Grid()
hover = (0, 0)
for x in range(15):
    for y in range(10):
        if random.random() > 0.3:
            g[x, y] = True


def draw():
    hn = list(g.neighbours(hover))
    screen.clear()
    for x in range(15):
        for y in range(10):
            wx, wy = g.coord_to_world((x, y))
            color = ON if g[x, y] else OFF
            draw_hex(wx * size, wy * size, color)
            if (x, y) in hn:
                draw_hex(wx * size, wy * size, HOVER, size=20)

    if path:
        p = (g.coord_to_world(h) for h in path)
        p = [(x * size, y * size) for x, y in p]
        for a, b in zip(p, p[1:]):
            screen.draw.line(a, b, PATH)

ps = deque(maxlen=2)
path = None
hover = (0, 0)


def on_mouse_move(pos):
    global hover
    hover = pixel_to_hex(*pos)


def on_mouse_down(pos, button):
    global path
    h = pixel_to_hex(*pos)
    if button == mouse.RIGHT:
        g[h] = not g[h]
    else:
        ps.append(h)
        if len(ps) == 2:
            try:
                path = g.find_path(*ps)
            except NoPath:
                path = None
