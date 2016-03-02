
class Faction:
    def __init__(self, name):
        self.name = name
        self.actors = []

    def add(self, actor):
        if actor.faction is not None:
            actor.faction.remove(actor)
        self.actors.append(actor)
        actor.faction = self

    def remove(self, actor):
        try:
            self.actors.pop(self.actors.index(actor))
        except ValueError:
            if actor.faction != self:
                assert False, "Can't remove actor {} from faction {} as it isn't a member".format(actor.name, self.name)

    def __iter__(self):
        return iter(self.actors)
