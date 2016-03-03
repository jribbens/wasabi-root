import random
from pyglet import clock
from lostcolony.pathfinding import HexGrid, HEX_HEIGHT, HEX_WIDTH
from lostcolony.animation import load


class Ricochet:
    FILENAMES = ['effects/ricochet-%d.png' % i for i in range(1, 5)]

    images = None

    @classmethod
    def load_images(cls):
        if cls.images is not None:
            return

        cls.images = []
        for fname in cls.FILENAMES:
            im = load(fname)
            im.anchor_x = im.width // 2
            im.anchor_y = im.height
            cls.images.append(im)

    def __init__(self, world, pos, duration=1.0):
        self.load_images()
        self.world = world
        self.pos = pos
        self.world.add_effect(self, pos)
        if duration is not None:
            clock.schedule_once(self.destroy, duration)

    def random_sprites(self, num=1):
        x, y = HexGrid.coord_to_world(self.pos)
        for _ in range(num):
            im = random.choice(self.images)
            dx = random.random() - 0.5
            dy = random.random() - 0.5
            c = x + dx, y + dy
            yield c, im

    def get_drawables(self):
        return self.random_sprites(random.randint(1, 5))

    def destroy(self, _):
        self.world.remove_effect(self, self.pos)


class ShotgunRicochet(Ricochet):
    def __init__(self, world, pos):
        super().__init__(world, pos, duration=0.3)
        self.drawables = list(self.random_sprites(5))

    def get_drawables(self):
        return self.drawables
