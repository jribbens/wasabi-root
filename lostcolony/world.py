
class World:
    """
    Top-level container for the map, factions, actors etc
    """

    def __init__(self, tmx, hex_grid):
        self.tmx = tmx
        self.hex_grid = tmx

    def get_actor(self, hex):
        # replace this with a sensible way to get them. What object can we interrogate?
        return None # to do
