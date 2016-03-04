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
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = radians(angle_deg)
            pts.append((
                HEX_WIDTH * 0.5 * cos(angle_rad),
                HEX_HEIGHT * 0.5 * sin(angle_rad)
            ))
        return pts
    pts = pts()

    MODE = gl.GL_LINES
    INDICES = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 0]

    def __init__(self, color, pos=(0, 0), batch=None):
        self.batch = batch or pyglet.graphics.Batch()
        self.list = self.batch.add_indexed(6, self.MODE, None, self.INDICES, 'v2f', ('c4B', as_color4(*color) * 6))
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
        self.batch.draw()


class FilledCursor(TileOutlineCursor):
    MODE = gl.GL_TRIANGLES
    INDICES = [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5]


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
