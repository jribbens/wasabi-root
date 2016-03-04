import math
import os.path
import pyglet.font
from pyglet.text import Label
from .tile_outline import TileOutlineCursor
from . import wave


def relpath(p):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), p)
    )

pyglet.font.add_file(relpath('../fonts/gun4fc.ttf'))


CURRENT_GOAL = '::: Proceed to complex'
GOAL_COLOUR = (255, 200, 100, 255)
GOAL_POS = 42, 19

DEFEND = '::: Motion detected'
DEFEND_COLOUR = (180, 0, 0, 255)

FONT = 'Gunship Condensed'


label = Label(
    CURRENT_GOAL,
    font_name=FONT,
    font_size=12,
    color=GOAL_COLOUR
)

marker_img = pyglet.image.load(relpath('../images/pois/direction.png'))
marker_img.anchor_x = marker_img.width
marker_img.anchor_y = marker_img.height // 2
outline = TileOutlineCursor(GOAL_COLOUR)
marker = pyglet.sprite.Sprite(marker_img)
marker.color = GOAL_COLOUR[:3]



def goal_is_onscreen(camera):
    x, y = GOAL_POS
    (cx1, cy1), (cx2, cy2) = camera.coord_bounds()
    return cy2 <= y < cy1 and cx1 <= x < cx2


def draw_outline(camera):
    """Draw the tile outline."""
    if goal_is_onscreen(camera):
        outline.pos = camera.coord_to_viewport(GOAL_POS)
        outline.draw()


def draw_marker(camera):
    """Draw a pointer indicating the direction of the goal."""
    if goal_is_onscreen(camera):
        return
    x, y = camera.coord_to_viewport(GOAL_POS)
    w, h = camera.viewport
    h -= 30
    w -= 10
    w2 = w / 2
    h2 = h / 2
    dx = x - w2
    dy = y - h2
    mag = math.sqrt(dx * dx + dy * dy)
    nx, ny = dx / mag, dy / mag

    angle = math.atan2(dy, dx)

    # Pyglet is so wrong - degrees clockwise?
    # Should be radians anticlockwise, surely?!
    marker.rotation = math.degrees(-angle)

    aspect = h / w
    tan = abs(ny) / abs(nx)

    if tan > aspect:
        ratio = h2 / abs(ny)
    else:
        ratio = w2 / abs(nx)

    y = h2 + round(ny * ratio) + 5
    x = w2 + round(nx * ratio) + 5
    marker.position = x, y
    marker.draw()


def display_goal(camera):
    """Draw the goal HUD."""
    w, h = camera.viewport
    label.x = 10
    label.y = h - 20
    if wave.current_wave:
        label.text = DEFEND
        label.color = DEFEND_COLOUR
    else:
        label.text = CURRENT_GOAL
        label.color = GOAL_COLOUR
        draw_marker(camera)
    label.draw()

