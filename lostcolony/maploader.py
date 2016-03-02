"""Functions for loading a game map from a TMX file.

PyTMX handles the format decoding; here we just unpack it into game structures.

"""
import re
import os
from collections import defaultdict

import pytmx
import pyglet.image

from lostcolony.pathfinding import HexGrid

# List an object here to make it not an obstruction
# otherwise all objects on the top layer will be treated as obstructions
NOT_OBSTRUCTIONS = set([
    # 'crate',
])

IMPASSABLE_FLOORS = re.compile(
    r'pool.*|water'
)


class Map:
    """Load a map from a TMX file."""
    def __init__(self, filename):
        self.floor = {}  # A list of floor graphics in draw order, keyed by coord
        self.objects = {}  # Static images occupying a tile, keyed by coord
        self.grid = HexGrid()
        self.images = {}
        self.load_file(filename)

    def load_file(self, mapfile):
        """Load a TMX file."""
        tmx = pytmx.TiledMap(mapfile)
        self.load_images(tmx)
        self.load_floor(tmx)
        self.load_objects(tmx)

    def load_floor(self, tmx):
        """Load the floor tiles.

        This also updates the pathfinding grid.

        """
        self.nlayers = len(tmx.layers)
        floor = defaultdict(list)
        for n, layer in enumerate(tmx.layers[:-1]):
            for x, y, (imgpath, *stuff) in layer.tiles():
                image = self.images[imgpath]
                floor[x, y].append(image)

                if IMPASSABLE_FLOORS.match(imgpath):
                    self.grid[x, y] = False
                else:
                    self.grid[x, y] = True
        self.floor = dict(floor)

    def load_objects(self, tmx):
        """Load all the static objects.

        This also updates the pathfinding grid.

        """
        self.objects = {}
        # Top layer contains object data
        for x, y, (imgpath, *_) in tmx.layers[-1].tiles():
            self.objects[x, y] = self.images[imgpath]

            if imgpath in NOT_OBSTRUCTIONS:
                self.grid[x, y] = True
            else:
                self.grid[x, y] = False

    def load_images(self, tmx):
        """Load a dictionary of tile images from the TiledMap given."""
        for image_data in tmx.images:
            if image_data:
                image, _, _ = image_data
                self.load_image(image)

    def load_image(self, name):
        path = os.path.abspath(name)
        im = self.images[name] = pyglet.image.load(path)
        im.anchor_x = im.width // 2
        im.anchor_y = 24
