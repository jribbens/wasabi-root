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


GOALS = [
    ('Look for research chief Dr Alonso', (42, 19)),
    ('Investigate dormitory', (48, 7)),
    ('Get medical provisions from stores', (43, 29)),
    ('Search lab computers for records', (63, 52)),
    ('Download files in server room', (77, 42)),
    ('Check for injured survivors in medbay', (75, 9)),
    ('Inspect operating room', (92, 6)),
    ('Activate sensor array', (79, 53)),
    ('Run scan for dinosaurs', (52, 47)),
    ('Follow trail at scientific site', (34, 59)),
    ('Follow trail in botanic garden', (34, 85)),
    ('Pursue dinos back to nest', (90, 84)),
    ('Return to shuttle', (15, 14)),
    ('Activate launch radar', (10, 70)),
    ('Return to shuttle', (15, 14)),
]

GOAL_COLOUR = (255, 200, 100, 255)

DEFEND = '::: Motion detected'
DEFEND_COLOUR = (180, 0, 0, 255)

FONT = 'Gunship Condensed'


goal_label = Label(
    GOALS[0][0],
    font_name=FONT,
    font_size=12,
    color=GOAL_COLOUR
)
defend_label = Label(DEFEND, font_name=FONT, font_size=12, color=DEFEND_COLOUR)

marker_img = pyglet.image.load(relpath('../images/pois/direction.png'))
marker_img.anchor_x = marker_img.width
marker_img.anchor_y = marker_img.height // 2
outline = TileOutlineCursor(GOAL_COLOUR)
marker = pyglet.sprite.Sprite(marker_img)
marker.color = GOAL_COLOUR[:3]


current_goal = -1
goal_pos = None


def next_goal():
    global current_goal, goal_pos, goal_text
    current_goal += 1
    goal_text, goal_pos = GOALS[current_goal]
    goal_label.text = '::: ' + goal_text


def goal_is_onscreen(camera):
    if not goal_pos:
        return False
    x, y = goal_pos
    (cx1, cy1), (cx2, cy2) = camera.coord_bounds()
    return cy2 <= y < cy1 and cx1 <= x < cx2


def draw_outline(camera):
    """Draw the tile outline."""
    if not goal_pos:
        return
    if goal_is_onscreen(camera):
        outline.pos = camera.coord_to_viewport(goal_pos)
        outline.draw()


def draw_marker(camera):
    """Draw a pointer indicating the direction of the goal."""
    if not goal_pos:
        return
    if goal_is_onscreen(camera):
        return
    x, y = camera.coord_to_viewport(goal_pos)
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
    if wave.current_wave:
        label = defend_label
    else:
        if not goal_pos:
            return
        label = goal_label
        draw_marker(camera)

    w, h = camera.viewport
    label.x = 10
    label.y = h - 20
    label.draw()

