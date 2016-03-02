from lostcolony.actor import Character, Actor
from lostcolony.animation import rex, raptor
from lostcolony.faction import Faction
from itertools import chain


OBSTRUCTIONS = {"bed",
                "bunk",
                "bunk2",
                "column",
                "crates1",
                "crates2",
                "crates3",
                "crates4",
                "desk1",
                "desk2",
                "lily1",
                "lily2",
                "medbay-bed",
                "medbay-bed2",
                "server",
                "server2",
                "short-wall",
                "shuttle-l",
                "shuttle-m",
                "shuttle-r",
                "table",
                "tree1",
                "uplink",
                "uplink-obj",
                "veg1",
                "veg2",
                "veg3",
                "veg4",
                "wall",
                }

class World:
    """
    Top-level container for the map, factions, actors etc
    """

    def __init__(self, grid):
        # TODO: un-hardcode this. can we set this in tiled?
        self.grid = grid

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
        return chain(*[faction.actors for faction in self.factions])

    def get_actors(self, hex):
        """Get a list of actors "in" the given tile."""
        return [a for a in self.actors if a.position == hex]

    def update(self, dt):
        for a in self.actors:
            a.update(dt)
