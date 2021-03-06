# encoding: utf-8

import logging

import pyglet

from lostcolony import audio
from lostcolony import behaviour
from lostcolony.pathfinding import (
    HEX_WIDTH, HEX_HEIGHT, NoPath
)
from lostcolony.effects import BloodSpray

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

    FACING_TO_DIR = {0: 'n', 1: 'ne', 2: 'se', 3: 's', 4: 'sw', 5: 'nw'}
    DIR_TO_FACING = {'n': 0, 'ne': 1, 'se': 2, 's': 3, 'sw': 4, 'nw': 5}

    DEFAULT_SPEED = 1.2

    alive = True


    def __init__(self, world, id, anim, position, faction, facing, hp=10, colour=(0, 0, 0)):
        """
        :param world:
        :param id: a string id for lookup purposes
        :param position: hex coordinates
        :param faction: the int used for FACING_TO_DIR etc
        :param facing: Hex side: 0 = top, 1 = top right ..; e.g. you're pointing at grid.neighbours()[facing]
        :param colour: colour used for fields of fire, only used for the player faction. Think of it as a brand value...
        :return:
        """
        # Integer coordinates of the actor
        # This attribute can be
        #   - None for still objects
        #   - A coordinate for the target, should be a neighbour of self.position
        self.anim = anim.create_instance()
        self.world = world
        self.id = id
        self.position = position

        self.faction = faction
        faction.add(self)
        assert 0 <= facing < 6
        self.facing = facing
        self.colour = colour

        self.total_hp = hp

        self.hp = hp

        self.walking_sound = None
        self.walk_fx = None

        self.moving_to = None
        self.walking_to = None
        # Non-integer progress of movement: 0.0 == just started, 1.0 == arrived
        self.progress = 0
        # Linear speed in tiles per second. non-negative
        self.speed = 0
        self.weapon = None

        self.action = 'stand'
        self.phase = ''

        # Default behavior:
        self.behaviour = behaviour.sequence(
            behaviour.die,
            behaviour.move_step
        )

        self.world.add(self, self.position)

    def update(self, t, dt):
        """Update, essentially moving"""
        if not self.alive:
            return
        self.behaviour(self, t, dt)
        self.anim.pos = self.position
        self.anim.direction = self.FACING_TO_DIR[self.facing]

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
        self.look(destination)

    def look(self, destination):
        """
        Update facing towards an adjacent square
        """
        # update direction
        delta = (destination[0] - self.position[0], destination[1] - self.position[1])
        direction = self.get_dir(delta)
        self.facing = self.DIR_TO_FACING[direction]
        self.anim.direction = direction

    def get_coords(self):
        """Cartesian (x, y) coords for this actor"""
        source = _coord_to_world(self.position)
        if self.moving_to is None:
            return source
        else:
            dest = _coord_to_world(self.moving_to)
            delta = (dest[0] - source[0], dest[1] - source[1])
            return source[0] + delta[0] * self.progress, source[1] + delta[1] * self.progress

    def get_dir(self, delta):
        """
        Use the delta difference to figure out the direction a character should face.

        :param delta: tuple, co-ordinate difference between current position and next position.
        """

        if delta[1] < 0:
            direction = 'n'
        elif delta[1] > 0:
            direction = 's'
        else:
            if self.position[0] % 2:
                direction = 's'
            else:
                direction = 'n'

        if delta[0] > 0:
            direction += 'e'
        elif delta[0] < 0:
            direction += 'w'

        return direction

    def hit(self, damage, max_value=10):
        """
        Receive some damage, manage the consequences

        :param damage: int
        :return:
        """
        # deduct damage taken
        self.hp = self.hp - damage
        BloodSpray(self.world, self.position, damage, max_value)
        if self.hp <= 0:
            self.death()

    def walk_to(self, target):
        self.walking_to = target
        self.anim.play('walk')
        audio.stop_walk(self.walking_sound)
        self.walking_sound = audio.start_walk(self.walk_fx)

    def get_health(self, x, y):
        if self.hp == self.total_hp:
            # Don't show the health bar if it's full
            return None

        vertex_list = pyglet.graphics.Batch()

        health_left = ((self.hp/self.total_hp) * 80) - 40

        vertex_list.add(4, pyglet.gl.GL_QUADS, None,
                        ('v2f', (x-41, y+79, x+41, y+79, x+41, y+86, x-41, y+86)),
                        ('c3B', (150, 150, 150)*4))

        vertex_list.add(4, pyglet.gl.GL_QUADS, None,
                        ('v2f', (x-40, y+80, x+40, y+80, x+40, y+85, x-40, y+85)),
                        ('c3B', (150, 0, 0)*4))

        vertex_list.add(4, pyglet.gl.GL_QUADS, None,
                        ('v2f', (x-40, y+80, x+health_left, y+80, x+health_left, y+85, x-40, y+85)),
                        ('c3B', (40, 180, 0)*4))

        return vertex_list

    def stop(self):
        self.walking_to = None
        self.anim.play('stand')
        audio.stop_walk(self.walking_sound)

    def drawable(self, sx, sy):
        # TODO: Add animation, use heading
        off_x, off_y = self.get_coords()
        base_x, base_y = _coord_to_world(self.position)
        new_x = sx + (off_x - base_x) * HEX_WIDTH / 2
        new_y = sy - (off_y - base_y) * HEX_HEIGHT / 2
        return new_x, new_y, self.anim.draw(), self.get_health(new_x, new_y)

    def death(self):
        """This Actor has run out of HP. Kill it."""
        self.world.kill_actor(self, self.faction)
        self.alive = False

    def __repr__(self):
        return "<%s %r>" % (type(self).__name__, self.id)


class Character(Actor):

    def __init__(self, world, id, anim, position, faction, facing, hp, colour, sound=None):
        """
        :param colour: rgb tuple used for field of fire display
        :return:
        """
        super().__init__(world, id, anim, position, faction, facing, hp, colour)
        self.walk_fx = sound
        # Default behavior:
        self.behaviour = behaviour.sequence(
            behaviour.die,
            behaviour.move_step,
            behaviour.pathfinding,
        )
