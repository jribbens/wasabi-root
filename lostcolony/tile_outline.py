import pyglet
from pyglet import gl

from lostcolony.pathfinding import (
    HexGrid, HEX_WIDTH, HEX_HEIGHT
)


class TileOutline:
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
        self.list = pyglet.graphics.vertex_list(7, 'v2f', ('c3B', color * 7))
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

    def set_hex(self, coord):
        self.pos(  )

    def draw(self):
        self.list.draw(gl.GL_LINE_STRIP)

