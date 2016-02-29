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


class PygletTiledMap:
    def __init__(self, window, mapfile):
        self.camera = (0, 0)   # The top-left of the viewport
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

    def load_image(self, name):
        path = os.path.abspath(name)
        im = self.images[name] = pyglet.image.load(path)
        im.anchor_x = im.width // 2
        im.anchor_y = im.height - HEX_HEIGHT // 2

    def draw(self):
        for n, layer in enumerate(self.tmx.layers):
            for x, y, image_data in layer.tiles():
                imgpath, _, _ = image_data
                image = self.images[imgpath]

                sx, sy = HexGrid.coord_to_screen((x, y))

                cx, cy = self.camera

                if (cx - HEX_WIDTH < sx < cx + self.window.width + HEX_HEIGHT * 2 and
                        cy - HEX_HEIGHT < sy < cy + self.window.height + HEX_HEIGHT * 2):
                    sprite = pyglet.sprite.Sprite(image, sx-cx, self.window.height-sy+cy)
                    sprite.draw()
        self.cursor.draw()

    def hover(self, x, y):
        """Set the position of the mouse cursor."""
        cx, cy = self.camera
        c = HexGrid.screen_to_coord((x + cx, self.window.height - y + cy))
        sx, sy = HexGrid.coord_to_screen(c)
        self.cursor.pos = sx - cx, self.window.height - sy + cy


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
        cam_x, cam_y = tmxmap.camera
        cam_x -= dx
        cam_y += dy
        tmxmap.camera = cam_x,cam_y
        print("drag", x, y, dx, dy, buttons)
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
