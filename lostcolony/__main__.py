import logging

import pyglet.app

import lostcolony.audio
import lostcolony.mapviewer

logging.basicConfig(level=logging.INFO)


def main():
    lostcolony.audio.init()
    pyglet.app.run()
    lostcolony.audio.quit()


if __name__ == '__main__':
    main()
