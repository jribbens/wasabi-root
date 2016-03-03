import pyglet
from pyglet import gl

from lostcolony.animation import load
from lostcolony.pathfinding import (
    HexGrid, HEX_WIDTH, HEX_HEIGHT
)

BASE_COLOR = (0, 0, 0, 255)


def as_color4(*color):
    """Convert the given color tuple to 4-tuple."""
    return color + BASE_COLOR[len(color):]


class TileOutlineCursor:
    """This class draws a hexagonal tile outline.

    The attribute pos can be used to move the outline around: this is
    currently a viewport coordinate (but a tile coordinate would naturally be
    a better fit).

    """
    def pts():
        """Calculate the points for a hexagon."""
        from math import radians, cos, sin
        pts = []
        for i in range(7):
            angle_deg = 60 * i
            angle_rad = radians(angle_deg)
            pts.append((
                HEX_WIDTH * 0.5 * cos(angle_rad),
                HEX_HEIGHT * 0.5 * sin(angle_rad)
            ))
        return pts
    pts = pts()

    def __init__(self, color, pos=(0, 0)):
        self.list = pyglet.graphics.vertex_list(7, 'v2f', ('c4B', as_color4(*color) * 7))
        self.pos = pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, v):
        self._pos = x, y = v
        pts = []
        for px, py in self.pts:
            pts.append(px + x)
            pts.append(py + y)
        self.list.vertices = pts

    def draw(self):
        self.list.draw(gl.GL_LINE_STRIP)


class FilledCursor(TileOutlineCursor):
    def draw(self):
        self.list.draw(gl.GL_POLYGON)


class ImageCursor(object):
    image = None

    @classmethod
    def load_image(cls):
        if cls.image:
            return
        im = cls.image = load(cls.FILENAME)
        im.anchor_x = im.width // 2
        im.anchor_y = im.height // 2

    def __init__(self, color, pos=(0, 0)):
        self.load_image()
        self.sprite = pyglet.sprite.Sprite(self.image)
        self.sprite.position = pos
        # TODO: honour color

    @property
    def pos(self):
        return self.sprite.position

    @pos.setter
    def pos(self, v):
        self.sprite.position = v

    def draw(self):
        self.sprite.draw()


class SelectionCursor(ImageCursor):
    FILENAME = 'ui/selected-pc.png'


class MoveCursor(ImageCursor):
    FILENAME = 'ui/move-to.png'
