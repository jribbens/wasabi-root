import sys
import time
sys.path.insert(0, '.')

import random
from math import cos, sin, radians, sqrt
from pathfinding import HexGrid, NoPath
from actor import Actor
from collections import deque

ON = 255, 255, 255
OFF = 255, 128, 128
PATH = 0, 255, 0
HOVER = 0, 128, 255,
TOKEN = 255, 255, 0,
LOS = 255, 0, 255,

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


g = HexGrid()
token = Actor(None)
hover = (0, 0)
for x in range(15):
    for y in range(10):
        if random.random() > 0.3:
            g[x, y] = True


def draw():
    hn = list(g.neighbours(hover))
    screen.clear()
    # Show actor
    ax, ay = token.get_coords()
    draw_hex(ax * size, ay * size, TOKEN, size=10)
    # Line of sight
    los_x, los_y = g.coord_to_world(hover)
    screen.draw.line((ax * size, ay * size), (los_x * size, los_y * size), LOS)
    obstacles = g.visible(token.position, hover, [None])

    # Show map
    for x in range(15):
        for y in range(10):
            wx, wy = g.coord_to_world((x, y))
            color = ON if g[x, y] else OFF
            draw_hex(wx * size, wy * size, color)
            # Show hovered squares
            if (x, y) in hn:
                draw_hex(wx * size, wy * size, HOVER, size=20)
            if (x, y) in obstacles:
                draw_hex(wx * size, wy * size, LOS, size=30)

    # Show path
    if path:
        p = (g.coord_to_world(h) for h in path)
        p = [(x * size, y * size) for x, y in p]
        for a, b in zip(p, p[1:]):
            screen.draw.line(a, b, PATH)


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
        try:
            path = g.find_path(token.moving_to or token.position, h)
        except NoPath:
            path = None


def update():
    # Move actor along path
    while token.moving_to is None and path:
        token.go(path[-1], 1)
        path.pop()
    t = time.perf_counter()
    dt = 1/60
    token.update(t, dt)
