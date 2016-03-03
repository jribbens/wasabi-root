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
            # Find closest unblocked location to attack
            attackable = [p for p in grid.neighbours(e) if not grid.blocked(p)]
            if attackable:
                actor.walking_to = min(attackable, key=distance_to_actor)
                break
            # Can not attack this enemy, try another
        if actor.walking_to is None:
            logger.info("%r has no enemies to chase!", actor)


def pathfinding(actor, t, dt):
    if actor.position == actor.walking_to:
        actor.walking_to = None
        actor.anim.play('stand')
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
            actor.hit(10)  # for testing hp
            actor.walking_to = None
            actor.anim.play('stand')
    # FIXME: animations should go back to the actor and not the behaviour?
    actor.anim.pos = actor.position
    actor.anim.direction = actor.FACING_TO_DIR[actor.facing]


def sequence(*bs):
    seq = tuple(bs)

    def composed(actor, t, dt):
        for b in seq:
            b(actor, t, dt)
    return composed
