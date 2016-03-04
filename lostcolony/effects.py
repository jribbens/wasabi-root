import random
from pyglet import clock
from lostcolony.pathfinding import HexGrid, HEX_HEIGHT, HEX_WIDTH
from lostcolony.animation import load


class Effect:
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

    def __init__(self, world, pos):
        self.load_images()
        self.world = world
        self.pos = pos
        self.world.add_effect(self, pos)


class Ricochet(Effect):
    """This is the ricochet effect for the autocannon."""

    def __init__(self, world, pos, duration=1.0):
        super().__init__(world, pos)
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
        return self.random_sprites()

    def destroy(self, _):
        self.world.remove_effect(self, self.pos)


class ShotgunRicochet(Ricochet):
    def __init__(self, world, pos):
        super().__init__(world, pos, duration=0.3)
        self.drawables = list(self.random_sprites(5))

    def get_drawables(self):
        return self.drawables


class FlyingSprite(tuple):
    def blit(self, x, y, _):
        img, z = self
        img.blit(x, y + z, 0)


class BloodSpray(Effect):
    POINTS = [10, 5, 3, 2, 1]
    FILENAMES = ['effects/blood-%d.png' % p for p in POINTS]
    V = 2

    def __init__(self, world, pos, value, max_value=10):
        super().__init__(world, pos)
        self.create_particles(value, max_value)
        clock.schedule(self.update)

    def create_particles(self, value, max_value):
        self.particles = []
        for points, img in zip(self.POINTS, self.images):
            if points > max_value:
                continue
            num, value = divmod(value, points)

            x, y = HexGrid.coord_to_world(self.pos)
            for _ in range(num):
                v = self.V
                vx = random.uniform(-v, v)
                vy = random.uniform(-v, v)
                z = 30
                vz = random.uniform(60, 100)
                self.particles.append((x + vx * 0.5, y + vy * 0.5, z, vx, vy, vz, img))
            if not value:
                break

    def update(self, dt):
        ps = []
        for x, y, z, vx, vy, vz, img in self.particles:
            uz = vz
            vz -= 200 * dt
            z += 0.5 * (uz + vz) * dt
            if z < 0:
                continue
            x += vx * dt
            y += vy * dt
            ps.append((x, y, z, vx, vy, vz, img))
        self.particles = ps

    def get_drawables(self):
        for x, y, z, *_, img in self.particles:
            yield (x, y), FlyingSprite((img, z))
