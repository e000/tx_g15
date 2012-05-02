import Image
import ImageSequence
import itertools
from .g15_screen import G15Screen, MAX_X, MAX_Y
from .g15_screen_mixins import LoopingCallMixin, InterruptableScreenMixin
from array import array

def loadImage(filename, invert = False):
    img = Image.open(filename).convert('1').convert('P').point(lambda i: i >= 250, '1')
    if not invert:
        img = img.point(lambda i: 1 ^ i)

    if img.size != (MAX_X, MAX_Y):
        img = img.resize((MAX_X, MAX_Y), Image.NEAREST)


    return array('B', img.getdata()).tostring()

def loadGif(filename, invert = False, th = 127):
    img = Image.open(filename)

    frames = []
    for frame in ImageSequence.Iterator(img):
        frame = frame.point(lambda i: i - 256 + 2* th).convert('1').convert('P').point(lambda i: i >= 250, '1')
        if frame.size != (MAX_X, MAX_Y):
            frame = frame.resize((MAX_X, MAX_Y), Image.NEAREST)
        if not invert:
            frame = frame.point(lambda i: 1 ^ i)
        frames.append(array('B', frame.getdata()).tostring())

    return frames, img.info['duration']


class G15PicScreen(G15Screen, InterruptableScreenMixin):
    def loadImage(self, filename, invert = False):
        self._buf = loadImage(filename, invert)

    def __repr__(self):
        return "<G15PicScreen(%s)>" % (self.__class__.__name__)

    def __str__(self):
        if isinstance(self._buf, array):
            return self._buf.tostring()
        return self._buf

    def __init__(self, *a, **kw):
        super(G15PicScreen, self).__init__(*a, **kw)

class G15GifScreen(G15PicScreen, LoopingCallMixin):
    _gen = None
    def loadImage(self, filename, invert = False, th = 127):
        frames, delay = loadGif(filename, invert, th)
        print delay / 1000.0
        self._gen = itertools.cycle(frames)
        self._loopingCall.updateFrequency = delay / 1000.0

    def updateScreen(self):
        if self._gen:
            self._buf = next(self._gen)
            self.display()
        else:
            self.onPause()

    def __repr__(self):
        return "<G15GifScreen(%s)>" % self.__class__.__name__

    def __init__(self, *a, **kw):
        G15PicScreen.__init__(self, *a, **kw)
        LoopingCallMixin.__init__(self)



