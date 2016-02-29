import os
import pyglet
import pytmx


window = pyglet.window.Window()
label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')


class PygletTiledMap:
    def __init__(self, window, mapfile):
        self.coords = (0, 0)
        self.tmx = pytmx.TiledMap(mapfile)
        self.window = window
        self.images = {}

        for image_data in self.tmx.images:
            if image_data:
                image, _, _ = image_data
                self.load_image(image)

    def load_image(self, name):
        path = os.path.abspath(name)
        self.images[name] = pyglet.image.load(path)

    def draw(self):
        self.window.clear()
        for n, (name, image) in enumerate(self.images.items()):
            sprite = pyglet.sprite.Sprite(image, (n % 4) * self.tmx.tilewidth * 1.1, 500 - ((n // 4) * self.tmx.tileheight * 1.1))
            sprite.draw()

tmxmap = PygletTiledMap(window, "maps/encounter-01.tmx")


@window.event
def on_draw():
    tmxmap.draw()


if __name__ == '__main__':
    pyglet.app.run()
