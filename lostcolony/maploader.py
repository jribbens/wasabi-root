"""Functions for loading a game map from a TMX file.

PyTMX handles the format decoding; here we just unpack it into game structures.

"""
import re
import os
from collections import defaultdict, namedtuple

import pytmx
import pyglet.image

from lostcolony.pathfinding import HexGrid

# List an object here to make it not an obstruction
# otherwise all objects on the top layer will be treated as obstructions
NOT_OBSTRUCTIONS = set([
    # 'crate',
])

IMPASSABLE_FLOORS = re.compile(
    r'/(pool.*|water)\.png$'
)

PCS_RE = re.compile(r'(?:^|/)(rex|tom|ping|matt)-[\w-]*\.png$')
TRIGGERS_RE = re.compile(r'(?:^|/)trigger(\d+).png$')

TriggerArea = namedtuple('TriggerArea', 'locs difficulty')


def group_connected(triggers):
    """Group the given list of triggers into connected sets."""
    groups = []
    ungrouped = set((x, y, difficulty) for (x, y), difficulty in triggers.items())
    while ungrouped:
        x, y, difficulty = ungrouped.pop()
        pos = x, y
        locs = [pos]
        queue = [pos]
        while queue:
            pos = queue.pop()
            for x, y in HexGrid.neighbours(pos):
                if (x, y, difficulty) in ungrouped:
                    ungrouped.discard((x, y, difficulty))
                    c = x, y
                    locs.append(c)
                    queue.append(c)
        groups.append(TriggerArea(locs, difficulty))

    groups_by_loc = {}
    for g in groups:
        for l in g.locs:
            groups_by_loc[l] = g
    return groups, groups_by_loc


class Map:
    """Load a map from a TMX file."""
    def __init__(self, filename):
        self.floor = {}  # A list of floor graphics in draw order, keyed by coord
        self.objects = {}  # Static images occupying a tile, keyed by coord
        self.grid = HexGrid()
        self.images = {}
        self.pois = {}
        self.triggers = {}
        self.load_file(filename)

    def load_file(self, mapfile):
        """Load a TMX file."""
        tmx = pytmx.TiledMap(mapfile)
        self.width = tmx.width
        self.height = tmx.height
        self.load_images(tmx)
        self.load_floor(tmx)
        self.load_objects(tmx)
        self.load_pois(tmx)

    def load_pois(self, mapfile):
        """Load points of interest."""
        poi_layer = [l for l in mapfile.layers if l.name == 'POIs'][0]
        triggers = {}
        for x, y, (imgpath, *stuff) in poi_layer.tiles():
            mo = PCS_RE.search(imgpath)
            if mo:
                self.pois[mo.group(1)] = (x, y)
                continue
            mo = TRIGGERS_RE.search(imgpath)
            if mo:
                triggers[x, y] = int(mo.group(1))
        self.trigger_groups, self.triggers = group_connected(triggers)

    def load_floor(self, tmx):
        """Load the floor tiles.

        This also updates the pathfinding grid.

        """
        self.nlayers = len(tmx.layers)
        floor = defaultdict(list)
        for n, layer in enumerate(tmx.layers):
            if layer.name in ['Objects', 'POIs']:
                continue
            for x, y, (imgpath, *stuff) in layer.tiles():
                image = self.images[imgpath]
                floor[x, y].append(image)

                # bit 0 blocks sight, bit 1 blocks movement
                self.grid.cells[x, y] = 2 if bool(IMPASSABLE_FLOORS.search(imgpath)) else 0
        self.floor = dict(floor)

    def load_objects(self, tmx):
        """Load all the static objects.

        This also updates the pathfinding grid.

        """
        self.objects = {}
        obj_layer = [l for l in tmx.layers if l.name == 'Objects'][0]
        for x, y, (imgpath, *_) in obj_layer.tiles():
            self.objects[x, y] = self.images[imgpath]

            # bit 0 blocks sight, 1 blocks movement so value 3 bloks both
            self.grid.cells[x, y] = 3 if imgpath not in NOT_OBSTRUCTIONS else 0

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
