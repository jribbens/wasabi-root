"""
Conceptually, the bit where the cte fuzzy proto-mamal picks up a dead T-Rex's jaws and begins his rampage...

Fortunately in this game you can't transfer weapons.

This class looks after things like when they fire, fields of fire, hit probability and the like.
It also indirectly manages their effects.
"""

import time
from world import World


class Weapon():
    def __init__(self, actor):
        self.actor = actor
        self.attack_time = time.perf_counter()
        self.setup_time = 0 # Seconds between stopping and attacking.
        self.seconds_per_attack = 1.0
        self.field_of_fire = [] # coordiates. Earlier in the list = higher priority.
        self.damage = 1

    def got_there(self, t):
        """
        The instant it becomes stationary after a move.
        """
        self.attack_time = self.setup_time + t

        # To do:
        # Refresh the field of fire
        # What about creatures which attack while moving?

    def update(self, t):
        if self.attack_time < t:
            self.attack_time = t + self.seconds_per_attack
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
        return True


    def select_targets(self):
        ret = []
        for hex in self.field_of_fire:
            target = self.actor.world.get_actor(hex)
            if target and self.valid_target(target):
                ret.append(target)
                if self.single:
                    return ret
        return ret


class