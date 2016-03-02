from lostcolony.actor import Character


class World:
    """
    Top-level container for the map, factions, actors etc
    """

    def __init__(self):
        # TODO: un-hardcode this. can we set this in tiled?
        rex = Character(self, "rex")
        rex.position = (5, 5)

        self.heroes = [rex]

    def drawables(self):
        return self.heroes

    def get_actor(self, hex):
        # replace this with a sensible way to get them. What object can we interrogate?
        for h in self.heroes:
            if h.position == hex:
                return h
