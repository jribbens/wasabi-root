# encoding: utf-8

import os
# Note: coordinates are in the "even-q vertical" layout in the terminology of
# http://www.redblobgames.com/grids/hexagons/#coordinates


# to do: too many versions of this code
def _coord_to_world(coord):
    """Convert a map coordinate to a Cartesian world coordinate."""
    cx, cy = coord
    wx = 3/2 * cx
    wy = 3 ** 0.5 * (cy - 0.5 * (cx & 1))
    return wx, wy


class Actor(object):
    """Some movable element in the map"""

    def __init__(self, world):
        """

        :param tmx: Used to obey terrain restrictions
        :return:
        """
        # Integer coordinates of the actor
        self.position = (0, 0)
        # This attribute can be
        #   - None for still objects
        #   - A coordinate for the target, should be a neighbour of self.position
        self.moving_to = None
        # Non-integer progress of movement: 0.0 == just started, 1.0 == arrived
        self.progress = 0
        # Linear speed in tiles per second. non-negative
        self.speed = 0
        self.weapon = None
        # FIXME: why does this need a world??
        self.world = world
        self.facing = 1  # Hex side: 0 = top, 1 = top right ..; e.g. you're pointing at hex_grid.neighbours()[facing]
        self.faction = None  # Faction object it belongs to

    def update(self, t, dt):
        """Update, essentially moving"""
        if self.moving_to is not None:
            if self.weapon is not None:
                self.weapon.update(t)
            self.progress += self.speed * dt
            if self.progress >= 1.0:
                # Got there
                if self.weapon:
                    self.weapon.got_there(t)
                self.position = self.moving_to
                self.moving_to = None
                self.speed = 0
                self.progress = 0

    def go(self, destination, speed):
        """
        Jump to another hex after a time delay. Normally adjacent.

        :param destination:
        :param speed: hexes per second
        :return:
        """
        assert self.progress == 0
        assert self.moving_to is None
        if self.position == destination:
            return
        self.moving_to = destination
        self.speed = speed
        if self.weapon:
            self.weapin.moving()

    def get_coords(self):
        """Cartesian (x, y) coords for this actor"""
        source = _coord_to_world(self.position)
        if self.moving_to is None:
            return source
        else:
            dest = _coord_to_world(self.moving_to)
            delta = (dest[0] - source[0], dest[1] - source[1])
            return (source[0] + delta[0] * self.progress, source[1] + delta[1] * self.progress)

    def hit(self, damage):
        """
        Receive some damage, manage the consequences

        :param damage: int
        :return:
        """
        pass


class Character(Actor):

    def __init__(self, world, name):
        # Note: name should match the sprite filenames
        self.name = name
        super().__init__(world)

    def drawable(self, sx, sy):
        # TODO: Add animation, use heading
        return sy, sx, os.path.join("images", "pc", "%s-se-walk1.png" % (self.name))
