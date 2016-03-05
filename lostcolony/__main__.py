import logging

import pyglet.app

import pygame  # For audio only

import lostcolony.mapviewer

logging.basicConfig(level=logging.INFO)

def main():
    pygame.init()
    pyglet.app.run()
    pygame.quit()


if __name__ == '__main__':
    main()
