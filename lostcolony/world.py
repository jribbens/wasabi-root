from collections import defaultdict
from lostcolony.actor import Character, Actor
from lostcolony.animation import rex, raptor
from lostcolony.faction import Faction
from itertools import chain


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

    def init_player(self):
        # Stub code - this should come from scenario set-up
        faction = Faction("Player")
        Character(self, rex, faction=faction, position=(5, 5), facing=4)
        Character(self, rex, faction=faction, position=(6, 5), facing=4)
        Actor(self, raptor, faction=faction, position=(7, 5), facing=3)  # pet dino
        return faction

    def init_npcs(self):
        # to do: get from scenario set-up
        targets = Faction("Targets for weapon testing")
        victim = Actor(self, raptor, position=(8,8), faction=targets, facing=3)
        return [targets]

    @property
    def actors(self):
        return chain.from_iterable(faction.actors for faction in self.factions)

    def get_actors(self, hex):
        """Get a list of actors "in" the given tile."""
        return self.actors_by_pos.get(hex) or []

    def update(self, dt):
        for a in self.actors:
            a.update(dt)
