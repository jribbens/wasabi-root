import random
from pyglet import clock

from lostcolony.actor import Actor
from lostcolony import animation
from lostcolony.faction import Faction
from lostcolony.weapon import Weapon
from lostcolony import behaviour


current_wave = None

DEFAULT_BEHAVIOUR = behaviour.sequence(
    behaviour.die,
    behaviour.move_step,
    behaviour.chase_closest_enemy,
    behaviour.pathfinding,
)


class Wave:
    """Trigger a wave of dinos to descend on the gang."""

    def __init__(self, camera, world, target_faction, attackers=10, spawn_interval=1):
        self.camera = camera
        self.world = world
        self.target_faction = target_faction
        self.faction = self.world.factions["Dinos"]
        self.attackers = attackers
        self.spawn_interval = spawn_interval
        self.spawned = []

    def start(self):
        if not self.target_faction.actors:
            # nothing to attack!
            return
        global current_wave
        current_wave = self

        pos = self.target_faction.actors[0].position
        reachable = self.world.grid.reachable(pos)

        (cx1, cy1), (cx2, cy2) = self.camera.coord_bounds()
        reachable = [(x, y) for x, y in reachable if not (cy2 - 1 <= y < cy1 + 4 and cx1 - 1 <= x < cx2 + 3)]
        self.spawn_points = random.sample(reachable, self.attackers // 3)

        self.spawn()
        self.poll_finished()

    def spawn(self, *_):
        pos = random.choice(self.spawn_points)
        if not self.world.actors_by_pos[pos]:
            self.attackers -= 1
            target = random.choice(self.target_faction.actors).position
            dino = Actor(
                self.world,
                "dino",
                animation.raptor,
                position=pos,
                faction=self.faction,
                facing=3)
            dino.DEFAULT_SPEED = 2.5
            dino.weapon = Weapon()
            dino.behaviour = DEFAULT_BEHAVIOUR
            self.spawned.append(dino)

        if self.attackers:
            clock.schedule_once(self.spawn, self.spawn_interval)

    def is_over(self):
        """Return True if this wave is over."""
        return (
            self.attackers == 0 and
            not any(a.alive for a in self.spawned)
        )

    def poll_finished(self, *_):
        """Poll periodically to see if the wave is over."""
        global current_wave
        if self.is_over():
            current_wave = None
        else:
            clock.schedule_once(self.poll_finished, 2)
