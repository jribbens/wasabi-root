from collections import namedtuple
import os

import pyglet

Frame = namedtuple('Frame', 'sprite offset')
Sequence = namedtuple('Sequence', 'frames next_sequence')

DEFAULT_FRAME_RATE = 1

loop = object()

class Animation:
    def __init__(self, sequences, frame_rate=DEFAULT_FRAME_RATE):
        self.sequences = sequences
        self.frame_rate = frame_rate

    def create_instance(self, character_name, pos=(0,0), direction='se'):
        return AnimationInstance(self, character_name, pos, direction)


class AnimationInstance:
    def __init__(self, animation, character_name, pos=(0,0), direction='se'):
        self.animation = animation
        self.name = character_name
        self.pos = pos
        self.direction = direction
        self.play('stand')
        pyglet.clock.schedule(self.next_frame, self.animation.frame_rate)

    def play(self, sequence_name):
        self.current_frame = 0
        self.playing = sequence_name
        self.sequence = self.animation.sequences[sequence_name]

    def next_frame(self, *args):
        self.current_frame += 1
        if self.current_frame >= len(self.sequence.frames):
            next = self.sequence.next_sequence
            if next is loop:
                self.current_frame = 0
            else:
                self.play(next)

    def draw(self):
        return os.path.join("images",
                            "pc",
                            "{name}-{dir}-{action}{phase}.png".format(name=self.name,
                                                                      dir=self.direction,
                                                                      action=self.playing,
                                                                      phase=self.sequence.frames[self.current_frame]))

    def destroy(self):
        pyglet.clock.unschedule(self.next_frame)

animated_character = Animation({
    'stand': Sequence(('',), loop),
    'walk': Sequence((1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4), loop),
    'shoot': Sequence(('',), loop)
})

