import os
import pyglet
import pytmx
from lostcolony.pathfinding import HexGrid
from collections import defaultdict


class PygletTiledMap:
    def __init__(self, window, mapfile):
        self.camera = (0, 0)
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
        self.window.clear()
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
                    sprite = pyglet.sprite.Sprite(image, sx, self.window.height-sy)
                    sprite.draw()


window = pyglet.window.Window(resizable=True)
tmxmap = PygletTiledMap(window, "maps/encounter-01.tmx")


@window.event
def on_draw():
    tmxmap.draw()


if __name__ == '__main__':
    pyglet.app.run()
