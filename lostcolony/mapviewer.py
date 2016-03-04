from itertools import chain
import logging
from functools import lru_cache

import pyglet
from pyglet import gl
from pyglet.window import key

from lostcolony.pathfinding import (
    HexGrid, HEX_WIDTH, HEX_HEIGHT
)
from lostcolony.tile_outline import FilledCursor, MoveCursor
from lostcolony.ui import UI
from lostcolony.world import World
from lostcolony.maploader import Map
from lostcolony import wave

logger = logging.getLogger(__name__)


class Camera:
    WSCALE = HEX_WIDTH / 2
    HSCALE = HEX_HEIGHT / 2

    def __init__(self, viewport, pos=(0, 0)):
        self.viewport = viewport
        self.pos = pos

    def pan(self, dx, dy):
        """Move the camera by a relative offset."""
        x, y = self.pos
        self.pos = x - dx, y + dy

    def centre(self, coord):
        """Re-centre the camera on the given coord."""
        sx, sy = HexGrid.coord_to_screen(coord)
        self.pos = (
            sx - self.viewport[0] // 2,
            sy - self.viewport[1] // 2,
        )

    def coord_to_viewport(self, coord):
        """Given a tile coordinate, get its viewport position."""
        cx, cy = self.pos
        wx, wy = HexGrid.coord_to_world(coord)
        sx, sy = HexGrid.coord_to_screen(coord)
        return (
            sx - cx,
            self.viewport[1] - sy + cy
        )

    def world_to_viewport(self, coord):
        wx, wy = coord
        cx, cy = self.pos
        vx = wx * self.WSCALE - cx
        vy = -(wy * self.HSCALE - cy - self.viewport[1])
        return vx, vy

    def viewport_to_world(self, coord):
        """Get the world coordinate for a viewport coordinate."""
        x, y = coord
        cx, cy = self.pos
        wx = (x + cx) / self.WSCALE
        wy = (self.viewport[1] - y + cy) / self.HSCALE
        return wx, wy

    def viewport_to_coord(self, coord):
        """Given a viewport coordinate, get the tile coordinate."""
        return HexGrid.world_to_coord(self.viewport_to_world(coord))

    def viewport_bounds(self):
        """Return the p1, p2 bounds of the viewport in screen space."""
        x, y = self.pos
        w, h = self.viewport
        return self.pos, (x + w, y + h)

    def coord_bounds(self):
        """Return the x1, y1, x2, y2 bounds of the viewport in map coords."""
        return self.viewport_to_coord((0, 0)), self.viewport_to_coord(self.viewport)

    def world_bounds(self):
        """Return the x1, y1, x2, y2 bounds of the viewport in world coords."""
        return self.viewport_to_world((0, 0)), self.viewport_to_world(self.viewport)


class Scene:
    def __init__(self, window, map):
        self.camera = Camera((window.width, window.height), pos=(0, 0))
        self.cursor = MoveCursor((255, 0, 0))
        self.window = window
        self.images = {}
        self.mouse_coords = (0, 0)

        self.floor = map.floor
        self.objects = map.objects
        self.grid = map.grid
        self.world = World(self.grid, pois=map.pois)

    floor_batch = None
    floor_batch_pos = None
    floor_groups = [
        pyglet.graphics.OrderedGroup(layer) for layer in range(10)
    ]

    def get_floor_batch(self):
        if self.floor_batch_pos == self.camera.pos:
            return self.floor_batch

        self.floor_batch_pos = self.camera.pos
        self.floor_batch = pyglet.graphics.Batch()
        self.floor_sprites = []
        (cx1, cy1), (cx2, cy2) = self.camera.coord_bounds()
        for y in range(cy2 - 1, cy1 + 4):
            for x in range(cx1 - 1, cx2 + 3):
                imgs = self.floor.get((x, y))
                if imgs:
                    sx, sy = self.camera.coord_to_viewport((x, y))
                    for i, img in enumerate(imgs):
                        self.floor_sprites.append(
                            pyglet.sprite.Sprite(img, sx, sy, batch=self.floor_batch, group=self.floor_groups[i])
                        )
        return self.floor_batch

    fof_pos = None

    @lru_cache()
    def fof_effect_cached(self, field_of_fire, colour):
        batch = pyglet.graphics.Batch()
        for hex in field_of_fire:
            pos = self.camera.coord_to_viewport(hex)
            FilledCursor(colour + (50,), pos, batch)
        return batch

    def get_fof_effect(self, field_of_fire, colour):
        if self.fof_pos != self.camera.pos:
            self.fof_effect_cached.cache_clear()
            self.fof_pos = self.camera.pos

        return self.fof_effect_cached(tuple(field_of_fire), colour)

    def draw(self):
        """Draw the floor and any decals."""
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glAlphaFunc(gl.GL_GREATER, 0.0)
        self.get_floor_batch().draw()

        if wave.current_wave:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
            for character in self.world.get_all_player_actors():
                if character.weapon and character.weapon.field_of_fire:
                    self.get_fof_effect(character.weapon.field_of_fire, character.colour).draw()
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.cursor.draw()

    def get_drawables(self):
        """Get a list of drawable objects.

        These objects need to be depth-sorted along with any game objects
        within the camera bounds, and drawn using painter's algorithm,

        TODO: Refactor this all into a scenegraph class that can manage both
        static graphics and game objects.

        """
        (cx1, cy1), (cx2, cy2) = self.camera.coord_bounds()
        objects = []
        modifiers = []
        for y in range(cy2 - 1, cy1 + 4):
            for x in range(cx1 - 1, cx2 + 3):
                c = x, y
                obj = self.objects.get(c)
                if obj is not None:
                    sx, sy = self.camera.coord_to_viewport(c)
                    objects.append((sy, sx, obj))

                for actor in self.world.get_actors((x, y)):
                    sx, sy = self.camera.coord_to_viewport((x, y))
                    sx, sy, pic, health = actor.drawable(sx, sy)
                    objects.append((round(sy), round(sx), pic))
                    if health:
                        modifiers.append(health)

                for effect in self.world.get_effects(c):
                    for c, im in effect.get_drawables():
                        sx, sy = self.camera.world_to_viewport(c)
                        objects.append((sy, sx, im))

        return objects, modifiers

    def hover(self, x, y):
        """Set the position of the mouse cursor."""
        self.mouse_coords = x, y
        self.update_cursor()

    def update_cursor(self):
        """Recalculate the cursor position from the mouse coords."""
        c = self.camera.viewport_to_coord(self.mouse_coords)
        self.cursor.pos = self.camera.coord_to_viewport(c)


FPS = 30
pyglet.clock.set_fps_limit(30)
window = pyglet.window.Window(resizable=True)
keys = key.KeyStateHandler()
window.push_handlers(keys)

game_map = Map("maps/world.tmx")
tmxmap = Scene(window, game_map)
ui = UI(tmxmap.world, tmxmap.camera)
tmxmap.camera.centre(ui.current_hero.position)

@window.event
def on_draw():
    window.clear()
    tmxmap.draw()
    ui.draw()

    drawables, modifiers = tmxmap.get_drawables()
    drawables.sort(reverse=True, key=lambda t: (t[0], t[1]))
    for y, x, img in drawables:
        img.blit(x, y, 0)
    for modifier in modifiers:
        modifier.draw()


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if pyglet.window.mouse.LEFT:
        # Drag screen
        tmxmap.camera.pan(dx, dy)
        tmxmap.hover(x, y)
    elif pyglet.window.mouse.RIGHT:
        # Select by area
        pass


@window.event
def on_mouse_motion(x, y, dx, dy):
    tmxmap.hover(x, y)
    mx, my = 0, 0
    if x < window.width * 0.05:
        mx = -1
    elif x > window.width * 0.95:
        mx = 1

    if y < window.height * 0.05:
        my = 1
    elif y > window.height * 0.95:
        my = -1

    tmxmap.camera_vector = mx, my


@window.event
def on_mouse_release(x, y, button, mods):
    """
    Placeholder for a click event.

    Currently tells the UI to send a guy walking

    :param x: x position
    :param y: y position
    """
    if pyglet.window.mouse.LEFT == button:
        c = tmxmap.camera.viewport_to_coord((x, y))
        if tmxmap.world.actors_by_pos[c]:  # an actor might exist here, we can't move there but we could select them.
            for actor in tmxmap.world.actors_by_pos[c]:
                if actor.faction.name == 'Player':  # If in the player faction they are selectable.
                    ui.select_by_name(actor.id)
                    break
            else:
                logger.info("No selectable character at {coord}".format(coord=c))
        else:
            ui.go((x,y))
    elif pyglet.window.mouse.RIGHT == button:
        show_reachable((x, y))


@window.event
def on_resize(*args):
    tmxmap.floor_batch_pos = None
    tmxmap.camera.viewport = window.width, window.height


def on_key_press(symbol, mods):
    if symbol == pyglet.window.key._1:
        ui.select_by_name("rex")
    if symbol == pyglet.window.key._2:
        ui.select_by_name("matt")
    if symbol == pyglet.window.key._3:
        ui.select_by_name("ping")
    if symbol == pyglet.window.key._4:
        ui.select_by_name("tom")
    if symbol == pyglet.window.key.TAB:
        ui.select_next_hero()
    if symbol == pyglet.window.key.Q or symbol == pyglet.window.key.LEFT:
        ui.rotate('Q')
    elif symbol == pyglet.window.key.E or symbol == pyglet.window.key.RIGHT:
        ui.rotate('E')
    elif symbol == pyglet.window.key.F9:
        world = tmxmap.world
        camera = tmxmap.camera
        if not wave.current_wave:
            wave.Wave(camera, world, world.factions['Player']).start()
# Using push_handlers to avoid breaking the other handler
window.push_handlers(on_key_press)


def update(dt):

    tmxmap.world.update(dt)

    if keys[key.W]:
        tmxmap.camera.pan(0, -20)
        tmxmap.update_cursor()
    if keys[key.S]:
        tmxmap.camera.pan(0, 20)
        tmxmap.update_cursor()
    if keys[key.A]:
        tmxmap.camera.pan(20, 0)
        tmxmap.update_cursor()
    if keys[key.D]:
        tmxmap.camera.pan(-20, 0)
        tmxmap.update_cursor()
# to be deleted:
#    ox, oy = tmxmap.camera
#    dx, dy = tmxmap.camera_vector
#
#    nx = ox + dx * dt * 500
#    ny = oy + dy * dt * 500
#
#    tmxmap.camera = nx, ny

pyglet.clock.schedule(update)
