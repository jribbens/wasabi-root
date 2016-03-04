from collections import defaultdict
from lostcolony.actor import Character, Actor
from lostcolony import animation
from lostcolony.faction import Faction
from itertools import chain
from lostcolony.weapon import Rifle, Weapon, Grenade, AutoCannon, SniperRifle
import time


class World:
    """
    Top-level container for the map, factions, actors etc
    """

    def __init__(self, grid):
        # TODO: un-hardcode this. can we set this in tiled?
        self.grid = grid
        self.actors_by_pos = defaultdict(set)
        self.effects_by_pos = defaultdict(set)
        self.grid.layers.insert(0, self.actors_by_pos)

        self.factions = {
            'Player': self.init_player(),
            'Dinos': Faction("Dinos")
        }

    def add(self, actor, pos):
        """Add an actor to the world at pos."""
        self.actors_by_pos[pos].add(actor)

    def remove(self, actor, pos):
        """Remove an actor from the world at pos."""
        self.actors_by_pos[pos].discard(actor)

    def add_effect(self, effect, pos):
        """Add an actor to the world at pos."""
        self.effects_by_pos[pos].add(effect)

    def remove_effect(self, effect, pos):
        """Remove an effect from the world at pos."""
        self.effects_by_pos[pos].discard(effect)

    def get_effects(self, pos):
        return self.effects_by_pos[pos]

    def move(self, actor, from_pos, to_pos):
        """Move an actor from from_pos to to_pos."""
        self.remove(actor, from_pos)
        self.add(actor, to_pos)

    def init_player(self):
        # Stub code - this should come from scenario set-up
        faction = Faction("Player")

        rex = Character(self,
            "rex",
            animation.rex,
            faction=faction,
            position = (5,5),
            facing=3,
            hp=100,
            colour = (255,215,0))
        rex.weapon = Rifle()

        tom = Character(self,
            "tom",
            animation.tom,
            faction=faction,
            position=(6,5),
            facing=3,
            hp=100,
            colour=(22, 44, 80))
        tom.weapon = Rifle()

        ping = Character(self,
            "ping",
            animation.ping,
            faction=faction,
            position=(7,5),
            facing=3,
            hp=80,
            colour=(22, 90, 200))
        ping.weapon = SniperRifle()

        matt = Character(self,
            "matt",
            animation.matt,
            faction=faction,
            position = (8,5),
            facing=3,
            hp=150,
            colour = (255,120,0))
        matt.weapon = AutoCannon()

        for actor in faction.actors:
            actor.weapon.got_there(0, actor)

        return faction

    @property
    def actors(self):
        return chain.from_iterable(faction.actors for faction in self.factions.values())

    def field_of_fire_colours(self):
        return (
            (actor, actor.colour,)
            for actor in self.factions['Player'].actors
            # if isinstance(actor, Character)
        )

    def drawables(self):
        return self.actors

    def get_actors(self, hex):
        """Get a list of actors "in" the given tile."""
        return self.actors_by_pos.get(hex) or []

    def kill_actor(self, actor, faction):
        """
        An actor has died, we need to clean up the references we have left.

        :param actor: Actor, dead actor.
        :param faction: Faction, faction actor belongs to.
        """
        self.factions[faction.name].remove(actor)
        self.remove(actor, actor.position)

    def get_all_player_actors(self):
        return self.factions['Player'].actors

    def update(self, dt):
        t = time.time()
        for a in self.actors:
            a.update(t, dt)
