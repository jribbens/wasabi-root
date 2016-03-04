import os.path
import pyglet.font
from pyglet.text import Label
from . import wave

pyglet.font.add_file(
    os.path.join(os.path.dirname(__file__), '../fonts/gun4fc.ttf')
)

CURRENT_GOAL = '::: Proceed to complex'
GOAL_COLOUR = (255, 200, 100, 255)


DEFEND = '::: Motion detected'
DEFEND_COLOUR = (180, 0, 0, 255)

FONT = 'Gunship Condensed'


label = Label(
    CURRENT_GOAL,
    font_name=FONT,
    font_size=12,
    color=GOAL_COLOUR
)


def display_goal(camera):
    w, h = camera.viewport
    label.x = 10
    label.y = h - 20
    if wave.current_wave:
        label.text = DEFEND
        label.color = DEFEND_COLOUR
    else:
        label.text = CURRENT_GOAL
        label.color = GOAL_COLOUR
    label.draw()
