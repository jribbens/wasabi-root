from collections import defaultdict
from lostcolony.actor import Character, Actor
from lostcolony import animation
from lostcolony.faction import Faction
from itertools import chain
from lostcolony.weapon import Rifle, Weapon, Grenade
import time


class World:
    """
    Top-level container for the map, factions, actors etc
    """

    def __init__(self, grid):
        # TODO: un-hardcode this. can we set this in tiled?
        self.grid = grid
        self.actors_by_pos = defaultdict(set)
        self.grid.layers.insert(0, self.actors_by_pos)

        self.factions = [self.init_player()]  # first faction is the player
        self.factions += self.init_npcs()

    def add(self, actor, pos):
        """Add an actor to the world at pos."""
        self.actors_by_pos[pos].add(actor)

    def remove(self, actor, pos):
        """Remove an actor from the world at pos."""
        self.actors_by_pos[pos].discard(actor)

    def move(self, actor, from_pos, to_pos):
        """Move an actor from from_pos to to_pos."""
        self.remove(actor, from_pos)
        self.add(actor, to_pos)

    def init_player(self):
        # Stub code - this should come from scenario set-up
        faction = Faction("Player")

        rex = Character(self, "rex", animation.rex, faction=faction, position = (5,5), facing=4, hp=100, colour = (255,215,0))
        rex.weapon = Rifle()

        dino = Character(self, "tom", animation.raptor, faction=faction, position = (6,5), facing=0, hp=25, colour = (0x40, 0x40, 0xC0))
        dino.DEFAULT_SPEED = 2.0
        dino.weapon = Weapon()

        #Actor(self, animation.raptor, faction=faction, position = (7,5), facing=3, colour = (20,20,20)) # pet dino

        return faction

    def init_npcs(self):
        # to do: get from scenario set-up
        targets = Faction("Targets for weapon testing")
        victim = Actor(self, "victim", animation.raptor, position=(8, 8), faction=targets, facing=3)
        chaser = Actor(self, "chaser", animation.raptor, position=(18, 18), faction=targets, facing=3)
        # This should be configured in the map, or prebuilt
        from lostcolony import behaviour
        chaser.behaviour = behaviour.sequence(
            behaviour.die,
            behaviour.move_step,
            behaviour.chase_closest_enemy,
            behaviour.pathfinding,
        )
        return [targets]

    @property
    def actors(self):
        return chain.from_iterable(faction.actors for faction in self.factions)

    def field_of_fire_colours(self):
        return (
            (actor, actor.colour,)
            for actor in self.factions[0].actors
            # if isinstance(actor, Character)
        )

    def drawables(self):
        return self.actors

    def get_actors(self, hex):
        """Get a list of actors "in" the given tile."""
        return self.actors_by_pos.get(hex) or []

    def get_all_player_actors(self):
        return self.factions[0].actors

    def update(self, dt):
        t = time.time()
        for a in self.actors:
            a.update(t, dt)
