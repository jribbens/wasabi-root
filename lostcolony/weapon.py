"""
Conceptually, the bit where the cte fuzzy proto-mamal picks up a dead T-Rex's jaws and begins his
rampage...

Fortunately in this game you can't transfer weapons.

This class looks after things like when they fire, fields of fire, hit probability and the like.
It also indirectly manages their effects.
"""
import random

from lostcolony.effects import Ricochet, ShotgunRicochet
from lostcolony.pathfinding import HexGrid
from lostcolony import audio


class Weapon:
    effect = None

    def __init__(self, seconds_per_attack=1.0, damage=1, single_target=True):
        self.attack_time = 0  # based on time.perf_counter(), you start ready to rumble
        self.setup_time = 0   # Seconds between stopping and attacking.
        self.seconds_per_attack = seconds_per_attack
        self.field_of_fire = []  # coordinates. Earlier in the list = higher priority.
        self.damage = damage
        self.single_target = single_target
        self.sound = None

    def moving(self):
        if self.setup_time > 0:
            self.attack_time += 10000  # hack for don't attack

    def got_there(self, t, actor):
        """
        The instant it becomes stationary after a move.
        """
        self.attack_time = self.setup_time + t
        self.reset_field_of_fire(actor)

    def reset_field_of_fire(self, actor):
        """
        Regenerate the prioritised list of legal target hexes
        :return: None

        This default implementation reflects melee fighters
        """
        self.field_of_fire = (
            actor.world.grid.hex_in_front(actor.position, actor.facing),
            actor.world.grid.hex_in_front(actor.position, (actor.facing + 1) % 6),
            actor.world.grid.hex_in_front(actor.position, (actor.facing + 5) % 6),
        )

    def update(self, t, actor):
        if self.attack_time < t:
            self.attack_time = t + self.seconds_per_attack
            self.attack(actor)

    def calc_damage(self,actor, target):
        """
        Override to make damage dependent on range, vulnerabilities etc
        :param victim:
        :return:
        """
        return self.damage

    def attack(self, attacking_actor):
        targets = self.select_targets(attacking_actor)
        for target in targets:
            target.hit(self.calc_damage(attacking_actor,target))
            attacking_actor.anim.play('shoot')
            if self.sound:
                audio.effects[self.sound].play()
        if self.effect:
            world = attacking_actor.world
            for p in targets:
                self.effect(world, p.position)
        return len(targets)

    def valid_target(self, actor, target):
        """
        Is this a valid target?

        Some weapons attack everythig in an area, others check faction rules
        Stub: implement in sub-classes
        :param target:
        :return: True means kill it!
        """
        return actor.faction is not target.faction

    def select_targets(self, actor):
        ret = []

        if self.field_of_fire is None:
            return ret

        for target_hex in self.field_of_fire:
            for target in actor.world.get_actors(target_hex):
                if target and self.valid_target(actor, target):
                    ret.append(target)
                    if self.single_target:
                        return ret
        return ret


class Teeth(Weapon):
    def calc_damage(self, actor, target):
        return random.randint(1, self.damage)


class Rifle(Weapon):
    effect = ShotgunRicochet

    def __init__(self):
        super().__init__(seconds_per_attack=1.0, damage=1, single_target=True)
        self.sound = "rifle_burst"

    def reset_field_of_fire(self, actor):
        min_range = 1
        max_range = 9
        self.field_of_fire = _field_of_fire_front_arc(min_range, max_range, actor)


    def calc_damage(self,actor, target):
        return random.randint(1,8)


class Grenade(Weapon):

    def __init__(self):
        super().__init__(seconds_per_attack = 5.0, damage = 4, single_target = True)
        self.setup_time = 1


    def reset_field_of_fire(self, actor):
        min_range = 4
        max_range = 7
        self.field_of_fire = _field_of_fire_front_arc(min_range, max_range, actor)

    def select_targets(self, world):
        """
        Ideally the grenade should select the hex affecting the most enemies.
        For now, chuck it directly at the nearest.
        :return:
        """
        super().select_targets(world)



class SniperRifle(Weapon):
    effect = ShotgunRicochet

    def __init__(self):
        super().__init__(seconds_per_attack = 3.0, single_target = True, damage=3)
        self.setup_time = 3
        self.sound = "sniper"

    def reset_field_of_fire(self, actor):
        min_range = 1
        max_range = 12
        self.field_of_fire = _field_of_fire_front_arc(min_range, max_range, actor)
        self.field_of_fire.reverse()

    def calc_damage(self,actor, target):
        range = HexGrid.distance(actor.position, target.position)
        return random.randint(1,int(self.damage * range))


class AutoCannon(Weapon):
    effect = Ricochet

    def __init__(self):
        super().__init__()
        self.setup_time = 0
        self.seconds_per_attack = 0.8
        self.single_target = True
        self.heat = 0
        self.overheated = False
        self.shot_effect_time = 0 # 0 means not shooting, else the time to display the next one.
        self.shot_coord = None # not shooting
        self.sound = 'autocannon'

    @property
    def damage(self):
        return random.randint(1, 16)

    @damage.setter
    def damage(self, v):
        pass

    def reset_field_of_fire(self, actor):
        grid = actor.world.grid
        coord = grid.hex_in_front(actor.position, actor.facing)
        if coord in grid.cells:
            self.field_of_fire = [coord] if grid.visible(actor.position, coord) else []

    def update(self, t, actor):
        """Create the sparkly shooing effect"""
        if self.shot_effect_time and self.shot_effect_time < t and self.shot_coord:
            try:
                coord = next(self.shot_coord)
                self.shot_effect_time = t + 0.07
                self.effect(actor.world, coord)
            except StopIteration:
                self.shot_coord = None

        super().update(t, actor)

    def attack(self, aggressor):
        """

        :param aggressor: The violent actor, not the victim
        :return: Number of targets engaged
        """
        max_heat = 9
        ok_heat = 4
        if self.heat > 0:
            self.heat -= 1
            if self.heat <= ok_heat:
                self.overheated = False
            elif self.heat > max_heat:
                self.overheated = True

        if aggressor.walking_to is not None:
            self.field_of_fire = []  # can't move and fire
            return 0

        targets = 0
        if not self.overheated:
            targets = super().attack(aggressor)
            if targets:
                self.heat += 4
                self.shot_effect_time = 1 # display it
                self.shot_coord = iter(self.field_of_fire)

        max_range = 8
        if self.field_of_fire and len(self.field_of_fire) < max_range:
            coord = aggressor.world.grid.hex_in_front(self.field_of_fire[-1], aggressor.facing)
            if aggressor.world.grid.visible(aggressor.position, coord):
                self.field_of_fire.append(coord)
        # self.effect(aggressor.world, self.field_of_fire[-1])

        return targets


class ShotGun(Weapon):
    def __init__(self, damage=2, **args):
        super().__init__(damage=damage, **args)
        self.sound = "shotgun"

    def reset_field_of_fire(self, actor):
        min_range = 1
        self.max_range = 5
        self.field_of_fire = _field_of_fire_front_arc(min_range, self.max_range, actor)

    def calc_damage(self,actor, target):
        range = HexGrid.distance(actor.position, target.position)
        return random.randint(1,int(self.damage * (self.max_range - range)))


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
    hex_in_front = actor.world.grid.hex_in_front
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

    grid = actor.world.grid
    return [
        c
        for c in coords
        if c in grid.cells  # on-map
        and grid.visible(actor.position, c)
    ]
