import os
import pyglet
import pytmx
from lostcolony.pathfinding import HexGrid
from collections import defaultdict


class PygletTiledMap:
    def __init__(self, window, mapfile):
        self.camera = (0, 0)
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
        self.images[name] = pyglet.image.load(path)

    def draw(self):
        for n, layer in enumerate(self.tmx.layers):
            for x, y, image_data in layer.tiles():
                imgpath, _, _ = image_data
                image = self.images[imgpath]

                tilewidth = self.tmx.tilewidth
                tileheight = self.tmx.tileheight

                wx, wy = HexGrid.coord_to_world((x, y))
                sx = wx * tilewidth / 2
                sy = wy * tileheight / 2

                cx, cy = self.camera

                if cx - tilewidth < sx < cx + self.window.width + tilewidth * 2 and cy - tileheight < sy < cy + self.window.height + tileheight * 2:
                    sprite = pyglet.sprite.Sprite(image, sx-cx, self.window.height-sy+cy)
                    sprite.draw()


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

if __name__ == '__main__':
    pyglet.app.run()
