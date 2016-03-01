import os
import pyglet
import pytmx
from lostcolony.pathfinding import (
    HexGrid, HEX_WIDTH, HEX_HEIGHT
)
from pyglet import gl
from collections import defaultdict


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

    def draw(self):
        self.list.draw(gl.GL_LINE_STRIP)


class Camera:
    WSCALE = HEX_WIDTH / 2
    HSCALE = HEX_HEIGHT / 2

    def __init__(self, viewport, pos=(0, 0)):
        self.viewport = viewport
        self.pos = pos

    def pan(self, dx, dy):
        """Move the camera by a relative offset."""
        x, y = self.pos
        self.pos = x - dx, y + dy

    def coord_to_viewport(self, coord):
        """Given a tile coordinate, get its viewport position."""
        cx, cy = self.pos
        wx, wy = HexGrid.coord_to_world(coord)
        sx, sy = HexGrid.coord_to_screen(coord)
        return (
            sx - cx,
            self.viewport[1] - sy + cy
        )

    def viewport_to_coord(self, coord):
        """Given a viewport coordinate, get the tile coordinate."""
        x, y = coord
        cx, cy = self.pos
        wx = (x + cx) / self.WSCALE
        wy = (self.viewport[1] - y + cy) / self.HSCALE
        return HexGrid.world_to_coord((wx, wy))

    def viewport_to_world(self, coord):
        """Get the world coordinate of the tile for a viewport coordinate."""
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
        self.camera = Camera((window.width, window.height), pos=(0, 0))
        self.clicked = TileOutline((255, 255, 0))
        self.cursor = TileOutline((255, 0, 0))
        self.window = window
        self.images = {}
        self.floor = {}  # A list of floor graphics in draw order, keyed by coord
        self.objects = {}  # Static images occupying a tile, keyed by coord

        self.load_file(mapfile)

    def load_file(self, mapfile):
        """Load a TMX file."""
        tmx = pytmx.TiledMap(mapfile)
        for image_data in tmx.images:
            if image_data:
                image, _, _ = image_data
                self.load_image(image)

        self.nlayers = len(tmx.layers)
        floor = defaultdict(list)
        for n, layer in enumerate(tmx.layers[:-1]):
            for x, y, (imgpath, *_) in layer.tiles():
                image = self.images[imgpath]
                floor[x, y].append(image)

        self.floor = dict(floor)

        self.objects = {}
        # Top layer contains object data
        for x, y, (imgpath, *_) in tmx.layers[-1].tiles():
            self.objects[x, y] = self.images[imgpath]

    def load_image(self, name):
        path = os.path.abspath(name)
        im = self.images[name] = pyglet.image.load(path)
        im.anchor_x = im.width // 2
        im.anchor_y = 24

    def draw(self):
        """Draw the floor and any decals."""
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glAlphaFunc(gl.GL_GREATER, 0.0)
        (cx1, cy1), (cx2, cy2) = self.camera.coord_bounds()
        objects = []
        for y in range(cy2 - 1, cy1 + 4):
            for x in range(cx1 - 1, cx2 + 3):
                imgs = self.floor.get((x, y))
                if imgs:
                    sx, sy = self.camera.coord_to_viewport((x, y))
                    for img in imgs:
                        img.blit(sx, sy, 0)
        self.cursor.draw()

    def get_drawables(self):
        """Get a list of drawable objects.

        These objects need to be depth-sorted along with any game objects
        within the camera bounds, and drawn using painter's algorithm,

        TODO: Refactor this all into a scenegraph class that can manage both
        static graphics and game objects.

        """
        (cx1, cy1), (cx2, cy2) = self.camera.coord_bounds()
        objects = []
        for y in range(cy2 - 1, cy1 + 4):
            for x in range(cx1 - 1, cx2 + 3):
                obj = self.objects.get((x, y))
                if obj:
                    sx, sy = self.camera.coord_to_viewport((x, y))
                    objects.append((sy, sx, obj))
        return objects

    def hover(self, x, y):
        """Set the position of the mouse cursor."""
        c = self.camera.viewport_to_coord((x, y))
        self.cursor.pos = self.camera.coord_to_viewport(c)

    def click(self, x, y):
        """
        Set the clicked square on the tmxmap.

        If we are clicking on the current clicked square, unclick it.

        :param x: x position
        :param y:  y position
        """
        c = self.camera.viewport_to_coord((x, y))
        new_clicked_pos = self.camera.coord_to_viewport(c)

        if self.clicked.pos == new_clicked_pos:
            self.clicked.pos = (0, 0)
        else:
            self.clicked.pos = new_clicked_pos


window = pyglet.window.Window(resizable=True)
tmxmap = PygletTiledMap(window, "maps/encounter-01.tmx")


@window.event
def on_draw():
    window.clear()
    tmxmap.draw()

    drawables = tmxmap.get_drawables()
    drawables.sort(reverse=True)
    for y, x, img in drawables:
        img.blit(x, y, 0)


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


@window.event
def on_mouse_release(*args):
    print(tmxmap.camera.pos)


@window.event
def on_mouse_press(x, y, *args):
    """
    Placeholder for a click event.

    Currently sets a clicked square on the tmxmap.

    :param x: x position
    :param y: y position
    """
    if pyglet.window.mouse.LEFT:
        tmxmap.click(x, y)


@window.event
def on_resize(*args):
    tmxmap.camera.viewport = window.width, window.height


@window.event
def on_text(key):
    """
    Pan the screen in a North, West, South or Easterly direction depending on a key press.

    Using on_text as it takes into consideration key holds - on_key_press does not.

    :param key: str, key being pressed.
    """
    if key == 'w':
        tmxmap.camera.pan(0, -20)
    elif key == 's':
        tmxmap.camera.pan(0, 20)
    elif key == 'a':
        tmxmap.camera.pan(20, 0)
    elif key == 'd':
        tmxmap.camera.pan(-20, 0)


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
