"""
Remembering the dead
"""

import random
from pyglet.text import Label
from pyglet.clock import schedule_interval, schedule_once
from collections import deque
from lostcolony.goals import FONT

# Mostly a mix of team members and roman poets
_name = [
    "Alfonso",
    "Moisset",
    "Pope",
    "Grazebrook",
    "Grusimus Rex",
    "Pollonius",
    "Octavian",
    "Marclelus",
    "Cicero",
    "Sarbiki",
    "Shearwood",
    "Prado",
    "Ribbens",
    "Aedituus",
    "Juvencus",
    "Horace",
    "Persius",
    "Lucan",
    "Bassus",
    "Grattius",
    "Manilius",
    "Ovid",
    "Virgil",
    "Commodian",
    "Corippus",
    "Cornificia",
    "Bavius",
    "Paulinus"
]

_epithet = [
    "magnificent",
    "wise",
    "terrible",
    "smelly",
    "swift",
    "slow",
    "glorious",
    "niggard",
    "cruel",
    "mad",
    "vague",
    "red",
    "green",
    "poet",
    "boring",
    "bitter",
    "confused",
    "tardy",
    "cuddly",
    "cruel",
    "acrobatic",
    "dancer",
    "ancient",
    "artistic",
    "hairy-headed",
    "grey",
    "ox-eyed",
    "powerful",
    "raptor heart",
    "mighty"
]

_epitaph = [
    "your children miss you",
    "loving father",
    "beloved forever",
    "your poems outlive you",
    "here I lie, but don't you cry, one day too you will die",
    "his spirit lives on",
    "his sipirit craves vengence",
    "it's only a scratch",
    "rest in peace",
    "I told you I was sick",
    "I need a pyramid!",
    "beloved father",
    "we miss you",
    "your spirit lives on",
    "dust to dust",
    "fossil forever",
    "I will be avenged!",
    "a pillar of the community",
    "once all heart, now just soul",
    "master of the jungle drums",
    "a poet's soul",
    "gentle and brave",
    "defender of his pack",
    "he kept his oath",
    "archaeologists' bane"
]

_credits = (
    # font size, following space (pixels) text
    (24, 1.0, "Development Team"),
    (16, 0.4, "Dan Pope, art & scrum master"),
    (16, 0.4, "Nick Sarbiki, development"),
    (16, 0.4, "Michael Grazebrook, armourer"),
    (16, 0.4, "Connor Shearwood, development"),
    (16, 0.4, "Daniel Moisset, development"),
    (16, 0.4, "Andre Prado, development"),
    (16, 0.9, "Jon Ribbens, development"),
    (24, 0.9, "Tools and Components"),
    (16, 0.6,  "Tiled"),
    (16, 0.6,  "Pyglet"),
    (18, 1.2, "Python"),
    (24, 0.8, "In memory of the dinosaurs"),
    (24, 1.0, "murdered for your enjoyment")
)

class Credits:
    def __init__(self, difficulties, camera):
        self.difficulties = difficulties
        self.counter = 0
        self.labels = deque()
        self.credit_it = self.credit_text()
        self.camera = camera
        schedule_interval(self.update_position, 0.013)
        schedule_once(self.update_text, 0)

    def update_position(self, dt, _=None):
        width, height = self.camera.viewport
        for label in self.labels:
            label.y += 1
            r,g,b,a = label.color
            a -= 1
            label.color = r,g,b,a,
        if self.labels:
            label = self.labels[0]
            r,g,b,a = label.color
            if label.y > height or a <= 0:
                self.labels.popleft()

    def update_text(self, dt, _=None):
        width, height = self.camera.viewport
        try:
            size, spacing_delay, text = next(self.credit_it)
            x=width//2
            y=height//4
            label = Label(
                text, x=x, y=y,
                anchor_x='center', anchor_y='center',
                font_size=size, font_name=FONT,
                color=(255, 200, 100, 255) #(180, 0, 0, 255) # (255,54,30, 255) # (177,207,169,255)
            )
            self.labels.append(label)
            schedule_once(self.update_text, spacing_delay)
        except StopIteration:
            pass


    def on_draw(self, camera):
        for label in self.labels:
            label.draw()


    def credit_text(self):
        yield (36, 1.0, 'Game over')
        yield (36, 0.8, 'Credits')
        for t in _credits:
            yield t
        for t in self._remember_dinos():
            yield t
        yield(12,0.5,"")
        yield (36, 20, 'The end')



    def _remember_dinos(self):
        for wave in self.difficulties:
            victims = self.difficulties[wave]["attackers"]
            yield (16, 0.9, "Wave {}, rest in peace".format(wave))

            name = random.sample(_name, victims)
            epithet = random.sample(_epithet, victims)
            epitaph = random.sample(_epitaph, victims)
            for dino in range(victims):
                yield 12, 0.4, "{} the {}, {}".format(name[dino], epithet[dino], epitaph[dino])
            yield  12, 0.4, ""



if __name__ == "__main__":
    DIFFICULTIES = {
        1: {
            "attackers": 12,
            "spawn_interval": 5
        }
    }

    c = Credits(DIFFICULTIES)
    for line in c._remember_dinos():
        print(line)
