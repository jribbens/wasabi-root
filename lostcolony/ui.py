class UI:

    def __init__(self, world):
        self.current_hero = None
        self.world = world

    def select_by_name(self, name):
        heroes = [h for h in world.heros if h.name == name]
        self.current_hero = heroes[0] if heroes else None

    def select_next_hero(self):
        if self.current_hero is None:
            self.current_hero = self.world.heroes[0]
        else:
            hs = self.world.heroes
            self.current_hero = hs[(hs.index(self.current_hero) + 1) % len(hs)]

    def go(self, target):
        if self.current_hero is not None:
            self.current_hero.walk_to(target)