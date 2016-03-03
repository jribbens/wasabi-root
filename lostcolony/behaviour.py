import logging

from lostcolony.pathfinding import HexGrid, NoPath

logger = logging.getLogger(__name__)


# Behaviour: plug in behaviours for actors. These are called as the update() function of actors
def null(actor, t, dt):
    pass


def die(actor, t, dt):
    if actor.hp <= 0:
        actor.death()


def move_step(actor, t, dt):
    # FIXME: weapon should be split away from this
    if actor.weapon is not None:
        actor.weapon.update(t, actor)
    # Moving
    if actor.moving_to is not None:
        actor.progress += actor.speed * dt
        if actor.progress >= 1.0:
            # Got there
            actor.world.move(actor, from_pos=actor.position, to_pos=actor.moving_to)
            actor.position = actor.moving_to
            actor.moving_to = None
            actor.speed = 0
            actor.progress = 0
            if actor.weapon:
                actor.weapon.got_there(t, actor)


def chase_closest_enemy(actor, t, dt):
    if actor.walking_to is None:
        grid = actor.world.grid
        enemies = [a.position for a in actor.world.actors if a.faction != actor.faction]
        distance_to_actor = lambda p: HexGrid.distance(p, actor.position)
        enemies.sort(key=distance_to_actor)
        # print([a.faction for a in actor.world.actors])
        for e in enemies:
            if distance_to_actor(e) < 2:
                # We're already there! adjacent are at distance sqrt3
                # Just change facing
                delta = (e[0] - actor.position[0], e[1] - actor.position[1])
                direction = actor.get_dir(delta)
                actor.facing = actor.DIR_TO_FACING[direction]
                actor.anim.direction = direction
                return
            # Find closest unblocked location to attack
            attackable = [p for p in grid.neighbours(e) if not grid.blocked(p)]
            if attackable:
                actor.walk_to(min(attackable, key=distance_to_actor))
                break
            # Can not attack this enemy, try another
        if actor.walking_to is None:
            logger.info("%r has no enemies to chase!", actor)


def pathfinding(actor, t, dt):
    if actor.position == actor.walking_to:
        actor.stop()
    if actor.moving_to is None and actor.walking_to is not None:
        # Plan path
        try:
            path = actor.world.grid.find_path(actor.position, actor.walking_to)
            next_tile = path[-2]
            # Go to next place in path
            actor.go(next_tile, actor.DEFAULT_SPEED)
        except NoPath:
            # Can't go there, just ignore
            logger.info("%s can not walk to %s", repr(actor), actor.walking_to)
            actor.stop()


def sequence(*bs):
    seq = tuple(bs)

    def composed(actor, t, dt):
        for b in seq:
            b(actor, t, dt)
    return composed
