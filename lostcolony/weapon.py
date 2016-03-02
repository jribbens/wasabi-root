"""
Conceptually, the bit where the cte fuzzy proto-mamal picks up a dead T-Rex's jaws and begins his rampage...

Fortunately in this game you can't transfer weapons.

This class looks after things like when they fire, fields of fire, hit probability and the like.
It also indirectly manages their effects.
"""

import time


class Weapon():
    def __init__(self, actor):
        self.actor = actor
        self.attack_time = 0 # based on time.perf_counter(), you start ready to rumble
        self.setup_time = 0 # Seconds between stopping and attacking.
        self.seconds_per_attack = 1.0
        self.field_of_fire = [] # coordiates. Earlier in the list = higher priority.
        self.damage = 1
        self.single_target = True

    def moving(self):
        if self.setup_time > 0:
            self.attack_time += 10000 # hack for don't attack

    def got_there(self, t):
        """
        The instant it becomes stationary after a move.
        """
        self.attack_time = self.setup_time + t
        self.reset_field_of_fire()

    def reset_field_of_fire(self):
        """
        Reset self.field_of_fire: prioritised list of possible target hexes
        :return: None

        This default implementation reflects melee fighters
        """
        adjacent = self.actor.world.hex_grid.neighbours(self.actor.position)
        facing = self.actor.facing
        self.field_of_fire = ( adjacent[facing], adjacent[(facing + 1) % 6], adjacent[(facing + 5) % 6], )


    def update(self, t):
        if self.attack_time < t:
            self.attack_time = t + self.seconds_per_attack
            self.attack()


    def attack(self):
        targets = self.select_targets()
        for target in targets:
            target.hit(self.damage)


    def valid_target(self, target):
        """
        Is this a valid target?

        Some weapons attack everythig in an area, others check faction rules
        Stub: implement in sub-classes
        :param target:
        :return: True means kill it!
        """
        return self.actor.faction != target.faction


    def select_targets(self):
        ret = []

        if self.field_of_fire is None:
            return ret

        for target_hex in self.field_of_fire:
            target = self.actor.world.get_actor(target_hex)
            if target and self.valid_target(target):
                ret.append(target)
                if self.single_target:
                    return ret
        return ret


class Rifle(Weapon):
    def __init__(self, actor):
        super().__init__(actor)
        self.setup_time = 0
        self.seconds_per_attack = 1.0
        self.damage = 1
        self.single_target = True

    def reset_field_of_fire(self):
        min_range = 1
        max_range = 9
        self.field_of_fire = _field_of_fire_front_arc(min_range, max_range, self.actor)


class Grenade(Weapon):
    def __init__(self, actor):
        super().__init__(actor)
        self.setup_time = 1
        self.seconds_per_attack = 5.0
        self.damage = 3
        self.single_target = True


    def reset_field_of_fire(self):
        min_range = 4
        max_range = 6
        self.field_of_fire = _field_of_fire_front_arc(min_range, max_range, self.actor)


class SniperRifle(Weapon):
    def __init__(self, actor):
        super().__init__(actor)
        self.setup_time = 3
        self.seconds_per_attack = 5.0
        self.damage = 7 # do to: range-based
        self.single_target = True


    def reset_field_of_fire(self):
        min_range = 1
        max_range = 12
        self.field_of_fire = _field_of_fire_front_arc(min_range, max_range, self.actor)


class AutoCannon(Weapon):
    def __init__(self, actor):
        super().__init__(actor)
        self.setup_time = 0
        self.seconds_per_attack = 1.0
        self.damage = 1
        self.single_target = True

    def valid_target(self):
        return True

    def reset_field_of_fire(self):
        adjacent = self.actor.world.hex_grid.neighbours(self.actor.position)
        facing = self.actor.facing
        field_of_fire = [ adjacent[facing] ] # NB list not tuple

    def attack(self):
        super().attack()

        assert len(self.field_of_fire > 0) # to do: debug only, remove for release. If this fails, fix the bug.

        coord = self.actor.world.hex_grid.frot_hex()
        if coord and self.actor.world.hex_grid.visible(self.actor.position, coord, None):
            self.field_of_fire.append( (x,y) )


def _field_of_fire_front_arc(min_range, max_range, actor):
    """
    Create a 120 degree arc of file. Hexes are in target priority order.

    :param min_range:
    :param max_range:
    :param actor:
    :return:
    """
    """
    :param min_range:
    :param max_range:
    :param actor:
    :return:
    """
    coords = []
    hex_in_front = actor.world.hex_grid.hex_in_front
    frontal_hex = actor.position
    facing = actor.facing

    for distance in range(min_range - 1):
        frontal_hex = hex_in_front(frontal_hex, facing)

    for distance in range(min_range, max_range):
        left_hex = right_hex = frontal_hex = hex_in_front(frontal_hex, facing)
        coords.append(frontal_hex)

        left_facing = (facing + 4) % 6
        for i in range(distance):
            left_hex = hex_in_front(left_hex, left_facing)
            coords.append(left_hex)

        right_facing = (facing + 2) % 6
        for i in range(distance):
            right_hex = hex_in_front(right_hex, right_facing)
            coords.append(right_hex)

    return [
        c
        for c in coords
        if c in actor.world.hex_grid # on-map
        and actor.world.hex_grid.visible(actor.position, c)
    ]
