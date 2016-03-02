from lostcolony.tile_outline import TileOutline

# Colors
CURRENT_HERO = (0, 255, 0)


class UI:

    def __init__(self, world, camera):
        self.current_hero = None
        self.world = world
        self.camera = camera
        self.selection = TileOutline(CURRENT_HERO)

    def select_by_name(self, name):
        f = [fac for fac in self.world.factions if fac.name == "Player"][0]
        heroes = [h for h in f if h.name == name]
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

    def draw(self):
        if self.current_hero is not None:
            sx, sy = self.camera.coord_to_viewport(self.current_hero.position)
            hx, hy, _ = self.current_hero.drawable(sx, sy)
            self.selection.pos = hx, hy
            self.selection.draw()