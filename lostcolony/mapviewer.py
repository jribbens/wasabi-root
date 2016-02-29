import os
import pyglet
import pytmx
from lostcolony.pathfinding import (
    HexGrid, HEX_WIDTH, HEX_HEIGHT
)
from pyglet import gl
from collections import defaultdict


class TileOutline:
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

    def __init__(self, pos=(0, 0)):
        self.list = pyglet.graphics.vertex_list(7, 'v2f')
        self.pos = pos
        self.color = (1, 0, 0, 1)

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
        gl.glColor4f(*self.color)
        self.list.draw(gl.GL_LINE_STRIP)
        gl.glColor4f(1, 1, 1, 1)


class Camera:
    WSCALE = HEX_WIDTH / 2
    HSCALE = HEX_HEIGHT / 2

    def __init__(self, viewport, pos=(0, 0)):
        self.viewport = viewport
        self.pos = pos

    def pan(self, dx, dy):
        x, y = self.pos
        self.pos = x - dx, y + dy

    def coord_to_viewport(self, coord):
        cx, cy = self.pos
        wx, wy = HexGrid.coord_to_world(coord)
        return (
            wx * self.WSCALE - cx,
            self.viewport[1] - wy * self.HSCALE + cy
        )

    def viewport_to_coord(self, coord):
        x, y = coord
        cx, cy = self.pos
        wx = (x + cx) / self.WSCALE
        wy = (self.viewport[1] - y + cy) / self.HSCALE
        return HexGrid.world_to_coord((wx, wy))

    def viewport_to_world(self, coord):
        return HexGrid.coord_to_world(self.viewport_to_coord(coord))

    def viewport_bounds(self):
        """Return the p1, p2 bounds of the viewport in screen space."""
        x, y = self.pos
        w, h = self.viewport
        return self.pos, (x + w, y + h)

    def coord_bounds(self):
        """Return the x1, y1, x2, y2 bounds of the viewport in map coords."""
        return self.viewport_to_coord((0, 0)), self.viewport_to_coord(self.viewport)


class PygletTiledMap:
    def __init__(self, window, mapfile):
        self.camera = Camera((window.width, window.height))
        self.cursor = TileOutline()
        # to be deleted:
        #  self.camera_vector = (0, 0)
        self.tmx = pytmx.TiledMap(mapfile)
        self.window = window
        self.images = {}

        for image_data in self.tmx.images:
            if image_data:
                image, _, _ = image_data
                self.load_image(image)

        self.nlayers = len(self.tmx.layers)
        self.grid = {}
        for n, layer in enumerate(self.tmx.layers):
            for x, y, image_data in layer.tiles():
                imgpath, _, _ = image_data
                image = self.images[imgpath]
                self.grid[n, x, y] = image

    def load_image(self, name):
        path = os.path.abspath(name)
        im = self.images[name] = pyglet.image.load(path)
        im.anchor_x = im.width // 2
        im.anchor_y = HEX_HEIGHT // 2

    def draw(self):
        (cx1, cy1), (cx2, cy2) = self.camera.coord_bounds()
        for n in range(self.nlayers):
            for y in range(cy2 - 2, cy1 + 2):
                for x in range(cx1 - 1, cx2 + 2):
                    img = self.grid.get((n, x, y))
                    if img:
                        sx, sy = self.camera.coord_to_viewport((x, y))
                        sprite = pyglet.sprite.Sprite(img, sx, sy)
                        sprite.draw()
        self.cursor.draw()

    def hover(self, x, y):
        """Set the position of the mouse cursor."""
        c = self.camera.viewport_to_coord((x, y))
        self.cursor.pos = self.camera.coord_to_viewport(c)


window = pyglet.window.Window(resizable=True)
window.push_handlers(pyglet.window.event.WindowEventLogger())
tmxmap = PygletTiledMap(window, "maps/encounter-01.tmx")


@window.event
def on_draw():
    window.clear()
    tmxmap.draw()


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if pyglet.window.mouse.LEFT:
        # Drag screen
        tmxmap.camera.pan(dx, dy)
    elif pyglet.window.mouse.RIGHT:
        # Select by area
        pass


@window.event
def on_mouse_motion(x, y, dx, dy):
    tmxmap.hover(x, y)
    mx, my = 0, 0
    if x < window.width * 0.05:
        mx = -1
    elif x > window.width * 0.95:
        mx = 1

    if y < window.height * 0.05:
        my = 1
    elif y > window.height * 0.95:
        my = -1

    tmxmap.camera_vector = mx, my

def update(_, dt):
    # print(_)
    pass
# to be deleted:
#    ox, oy = tmxmap.camera
#    dx, dy = tmxmap.camera_vector
#
#    nx = ox + dx * dt * 500
#    ny = oy + dy * dt * 500
#
#    tmxmap.camera = nx, ny

pyglet.clock.schedule(update, 1/60)
