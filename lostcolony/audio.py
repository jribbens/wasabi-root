import os

import pygame  # We use pygame for audio, pyglet has some issues

effects = {}

def init():
    pygame.init()
    normal_music()
    for fx in "sniper rifle_burst shotgun".split():
        effects[fx] = pygame.mixer.Sound(os.path.join("sounds", "%s.wav" % fx))


def normal_music():
    pygame.mixer.music.load(os.path.join("music", "Swamplandia.ogg"))
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)

def action_music():
    pygame.mixer.music.load(os.path.join("music", "Swamplandia.ogg"))
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)

def quit():
    pygame.quit()