import os

import pygame  # We use pygame for audio, pyglet has some issues

def init():
    pygame.init()
    normal_music()

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