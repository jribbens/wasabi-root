from lostcolony.tile_outline import SelectionCursor

# Colors
CURRENT_HERO = (0, 255, 0)


class UI:

    def __init__(self, world, camera):
        self.current_hero = None
        self.world = world
        self.camera = camera
        self.selection = SelectionCursor(CURRENT_HERO)
        self.select_next_hero()

    def select_by_name(self, name):
        f = [fac for fac in self.world.factions if fac.name == "Player"][0]
        heroes = [h for h in f if h.id == name]
        self.current_hero = heroes[0] if heroes else None

    def select_next_hero(self):
        f = [fac for fac in self.world.factions if fac.name == "Player"][0]
        hs = list(f)
        if self.current_hero is None:
            self.current_hero = hs[0]
        else:
            self.current_hero = hs[(hs.index(self.current_hero) + 1) % len(hs)]

    def go(self, target):
        if self.current_hero is not None:
            c = self.camera.viewport_to_coord(target)
            self.current_hero.walk_to(c)

    def rotate(self, symbol):
        """
        Rotate a player left (q) or right (e) on keypress.

        Once rotated update the field of fire.

        :param symbol: str, key used (q or e)
        """
        if symbol == 'Q':
            self.current_hero.facing = (self.current_hero.facing - 1) % 6
        elif symbol == 'E':
            self.current_hero.facing = (self.current_hero.facing + 1) % 6

        if self.current_hero.weapon:
            self.current_hero.weapon.reset_field_of_fire(self.current_hero)

    def draw(self):
        if self.current_hero is not None:
            sx, sy = self.camera.coord_to_viewport(self.current_hero.position)
            hx, hy, *_ = self.current_hero.drawable(sx, sy)
            self.selection.pos = hx, hy
            self.selection.draw()
