from collections import namedtuple
import os

import pyglet


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), '../images')

DEFAULT_FRAME_RATE = 0.15

loop = object()


def load(impath):
    """Load a single image from the images/ directory."""
    path = os.path.join(RESOURCE_DIR, impath)
    return pyglet.image.load(path)


class Sequence:
    """A sequence is a set of frames.

    The base implementation does not have a facing.

    """
    @classmethod
    def load(cls, tmpl, num, next=loop, anchor_x=0, anchor_y=0):
        frames = [load(tmpl.format(n=i)) for i in range(1, num + 1)]
        for f in frames:
            f.anchor_x = anchor_x
            f.anchor_y = anchor_y
        return cls(frames, next)

    def __init__(self, frames, next_sequence):
        self.frames = frames
        self.next_sequence = next_sequence

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, key):
        """Get a frame.

        Key must be a tuple (facing, frame).

        """
        facing, frame = key
        return self.frames[frame]


class DirectionalSequence(Sequence):
    """An implementation of a sequence that has 6 directions."""
    DIRECTIONS = 'n ne se s sw nw'.split()

    @classmethod
    def load(cls, tmpl, num, next=loop, anchor_x=0, anchor_y=0):
        frames = {}
        for dir in cls.DIRECTIONS:
            fs = [load(tmpl.format(n=i, dir=dir)) for i in range(1, num + 1)]
            for f in fs:
                f.anchor_x = anchor_x
                f.anchor_y = anchor_y
            frames[dir] = fs
        return cls(frames, num, next)

    def __init__(self, frames, length, next_sequence):
        super().__init__(frames, next_sequence)
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        """Get a frame.

        Key must be a tuple (facing, frame).

        """
        facing, frame = key
        return self.frames[facing][frame]


class Animation:
    def __init__(
            self, sequences,
            default='default',
            frame_rate=DEFAULT_FRAME_RATE):
        self.sequences = sequences
        self.frame_rate = frame_rate
        self.default = default

    def create_instance(self, pos=(0, 0)):
        return AnimationInstance(self, pos)


class AnimationInstance:
    def __init__(self, animation, pos=(0, 0), direction='s'):
        self.animation = animation
        self.pos = pos
        self.play(animation.default)
        self.direction = direction
        pyglet.clock.schedule_interval(self.next_frame, self.animation.frame_rate)

    def play(self, sequence_name):
        """
        Start the sequence for a specified animation.

        Set current_frame to 0 to start.

        :param sequence_name: str, animation we are playing
        """
        self.current_frame = 0
        self.playing = sequence_name
        self.sequence = self.animation.sequences[sequence_name]

    def next_frame(self, *args):
        """
        Called by the clock.

        Move to the next frame of the animation.
        """
        self.current_frame += 1
        if self.current_frame >= len(self.sequence):
            next = self.sequence.next_sequence
            if next is loop:
                # We want to loop this animation infinitely, so go back to
                # the beginning.
                self.current_frame = 0
            else:
                self.play(next)

    def draw(self):
        """Returns the pyglet.graphics.Image representing the current frame."""
        return self.sequence[self.direction, self.current_frame]

    def destroy(self):
        pyglet.clock.unschedule(self.next_frame)


kw = dict(anchor_x=46, anchor_y=10)
rex = Animation({
        'stand': DirectionalSequence.load('pc/rex-{dir}-stand.png', 1, **kw),
        'walk': DirectionalSequence.load('pc/rex-{dir}-walk{n}.png', 4, **kw),
        'shoot': DirectionalSequence.load('pc/rex-{dir}-shoot.png', 1, next='stand', **kw),
    },
    default='stand'
)

raptor = Animation({
        'stand': DirectionalSequence.load('mobs/raptor-{dir}-stand.png', 1, anchor_x=64, anchor_y=32),
        'walk': DirectionalSequence.load('mobs/raptor-{dir}-walk{n}.png', 4, anchor_x=64, anchor_y=32),
    },
    default='stand',
    frame_rate=0.1
)
