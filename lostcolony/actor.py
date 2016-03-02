# encoding: utf-8

import os
import logging

from lostcolony.pathfinding import (
    HEX_WIDTH, HEX_HEIGHT, NoPath
)
# Note: coordinates are in the "even-q vertical" layout in the terminology of
# http://www.redblobgames.com/grids/hexagons/#coordinates


logger = logging.getLogger(__name__)


# to do: too many versions of this code
def _coord_to_world(coord):
    """Convert a map coordinate to a Cartesian world coordinate."""
    cx, cy = coord
    wx = 3/2 * cx
    wy = 3 ** 0.5 * (cy - 0.5 * (cx & 1))
    return wx, wy


class Actor(object):
    """Some movable element in the map"""

    FACING_TO_DIR = {1: 'n', 2: 'ne', 3: 'se', 4: 's', 5: 'sw', 6: 'nw'}
    DIR_TO_FACING = {'n': 1, 'ne': 2, 'se': 3, 's': 4, 'sw': 5, 'nw': 6}

    def __init__(self, world, anim, position, faction, facing):
        """

        :param world:
        :param anim:
        :param position:
        :param faction:
        :param facing: Hex side: 0 = top, 1 = top right ..; e.g. you're pointing at hex_grid.neighbours()[facing]
        :return:
        """
        # Integer coordinates of the actor
        # This attribute can be
        #   - None for still objects
        #   - A coordinate for the target, should be a neighbour of self.position
        self.anim = anim.create_instance()
        self.world = world
        self.position = position
        self.faction = faction
        faction.add(self)
        self.facing = facing

        self.moving_to = None
        # Non-integer progress of movement: 0.0 == just started, 1.0 == arrived
        self.progress = 0
        # Linear speed in tiles per second. non-negative
        self.speed = 0
        self.weapon = None
        # FIXME: why does this need a world??

        self.faction = None  # Faction object it belongs to
        self.action = 'stand'
        self.phase = ''

    def update(self, dt):
        """Update, essentially moving"""
        if self.moving_to is not None:
            if self.weapon is not None:
                self.weapon.update(dt)
            self.progress += self.speed * dt
            if self.progress >= 1.0:
                # Got there
                if self.weapon:
                    self.weapon.got_there()
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
            self.weapon.moving()

    def get_coords(self):
        """Cartesian (x, y) coords for this actor"""
        source = _coord_to_world(self.position)
        if self.moving_to is None:
            return source
        else:
            dest = _coord_to_world(self.moving_to)
            delta = (dest[0] - source[0], dest[1] - source[1])

            self.get_dir(delta)

            return source[0] + delta[0] * self.progress, source[1] + delta[1] * self.progress

    def get_dir(self, delta):
        """
        Use the delta difference to figure out the direction a character should face.

        :param delta: tuple, co-ordinate difference between current position and next position.
        """

        direction = ''

        if delta[1] < 0:
            direction += 'n'
        elif delta[1] > 0:
            direction += 's'
        else:
            direction += self.FACING_TO_DIR[self.facing][0]

        if delta[0] > 0:
            direction += 'e'
        elif delta[0] < 0:
            direction += 'w'

        self.facing = self.DIR_TO_FACING[direction]
        self.anim.direction = direction

    def hit(self, damage):
        """
        Receive some damage, manage the consequences

        :param damage: int
        :return:
        """
        pass

    def walk_to(self, target):
        logger.warn("I can't walk! you put a non-Character() in the player faction! ,%s", repr(self))

    def drawable(self, sx, sy):
        # TODO: Add animation, use heading
        off_x, off_y = self.get_coords()
        base_x, base_y = _coord_to_world(self.position)
        new_x = sx + (off_x - base_x) * HEX_WIDTH / 2
        new_y = sy - (off_y - base_y) * HEX_HEIGHT / 2
        return new_x, new_y, self.anim.draw()


class Character(Actor):

    DEFAULT_SPEED = 1.2

    def __init__(self, world, anim, position, faction, facing):
        super().__init__(world, anim, position, faction, facing)
        self.walking_to = None

    def get_pic(self):
        return self.anim.draw()

    def walk_to(self, target):
        self.walking_to = target
        self.anim.play('walk')

    def update(self, dt):
        super().update(dt)
        if self.position == self.walking_to:
            self.walking_to = None
            self.anim.play('stand')
        if self.moving_to is None and self.walking_to is not None:
            # Plan path
            try:
                path = self.world.grid.find_path(self.position, self.walking_to)
                next_tile = path[-2]
                # Go to next place in path
                self.go(next_tile, self.DEFAULT_SPEED)
            except NoPath:
                # Can't go there, just ignore
                logger.info("%s can not walk to %s", repr(self), self.walking_to)
                self.walking_to = None
                self.anim.play('stand')
        self.anim.pos = self.position
        self.anim.direction = self.FACING_TO_DIR[self.facing]
