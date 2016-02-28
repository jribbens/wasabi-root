import sys
import os
sys.path.insert(0, '.')

from math import cos, sin, radians, sqrt
from pathfinding import Grid

ON = 255, 255, 255
OFF = 255, 128, 128

size = 36.0

root3 = sqrt(3)


def draw_hex(x, y, color):
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


def draw():
    for x in range(15):
        for y in range(10):
            wx, wy = g.coord_to_world((x, y))
            color = ON if g[x, y] else OFF
            draw_hex(wx * size, wy * size, color)


def on_mouse_down(pos):
    h = pixel_to_hex(*pos)
    g[h] = not g[h]

