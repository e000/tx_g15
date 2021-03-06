from array import array
import Image, ImageDraw
from contextlib import contextmanager
import textwrap
from .util.FixedList import FixedList

MAX_CHARS_PER_LINE = 27

PIXEL_ON = 1
PIXEL_OFF = 0

MAX_X = 160
MAX_Y = 43
MAX_BUFFER_LENGTH = MAX_X * MAX_Y



class G15Screen(object):
    """
        A class that holds a given "Screen" that can be sent to g15daemon for display on the device.
    """
    _protocol = None

    def __init__(self, parent = None):
        self.clearScreen()
        if parent:
            self._protocol = parent

    def setPixel(self, x, y, state):
        """
            Sets a pixel at x, y to state -> {PIXEL_ON, PIXEL_OFF}

            Raises AssertionError if coordinates are out of range, or state is not valid
        """
        assert state in (PIXEL_OFF, PIXEL_ON) and 0 <= x < MAX_X and 0 <= y < MAX_Y

        self._buf[x + y * MAX_X] = state

    def clearScreen(self):
        """
            Clears the screen, setting all pixels to PIXEL_OFF
        """
        self._buf = array('B', [PIXEL_OFF] * MAX_BUFFER_LENGTH)

    def fillScreen(self):
        """
            Fills the screen, setting all pixels to PIXEL_ON
        """
        self._buf = array('B', [PIXEL_ON] * MAX_BUFFER_LENGTH)

    def __str__(self):
        """
            Converts the screen to its string representation to be sent over the wire to g15daemon.
        """
        return self._buf.tostring()

    def __repr__(self):
        return "<%s (PIXEL_ON = %i, PIXEL_OFF = %i)>" % (
            self.__class__.__name__, self._buf.count(PIXEL_ON), self._buf.count(PIXEL_OFF)
        )

    def display(self):
        """
            Sends the screen to the protocol, just a convenience function.
        """
        if self._protocol:
            self._protocol.sendScreen(self)

class G15CanvasScreen(G15Screen):
    """
        A screen that supports canvas options via ImageDraw.
    """

    def __init__(self, parent = None):
        self._protocol = parent
        self._img = Image.new('P', (MAX_X, MAX_Y))
        self._draw = ImageDraw.Draw(self._img)


    def display(self):
        self._buf = array('B', self._img.getdata())
        super(G15CanvasScreen, self).display()

    def clearScreen(self):
        self._draw.rectangle((0, 0, MAX_X, MAX_Y), fill = 0)

    bitmap = lambda self, *a, **kw: self._draw.bitmap(*a, **kw)
    line = lambda self, *a, **kw: self._draw.line(*a, **kw)
    chord = lambda self, *a, **kw: self._draw.chord(*a, **kw)
    ellipse = lambda self, *a, **kw: self._draw.ellipse(*a, **kw)
    pieslice = lambda self, *a, **kw: self._draw.pieslice(*a, **kw)
    point = lambda self, *a, **kw: self._draw.point(*a, **kw)
    polygon = lambda self, *a, **kw: self._draw.polygon(*a, **kw)
    rectangle = lambda self, *a, **kw: self._draw.rectangle(*a, **kw)
    text = lambda self, *a, **kw: self._draw.text(*a, **kw)



class G15TextScreen(G15CanvasScreen):
    """
        A Screen that has methods to allow for easy writing of text to the screen.
        Supports 5 lines of text.
    """

    def __init__(self, parent=None):
        super(G15TextScreen, self).__init__(parent)
        self._text = FixedList(5)

    def clear(self, clear_text = True):
        """
            Draws a blank rectangle over the canvas and clears the text buffer.
        """
        self._draw.rectangle((0, 0, MAX_X, MAX_Y), fill = 0)

        if clear_text:
            self._text.clear()

    def appendLine(self, text, center = False):
        """
            Appends line of text to the screen

            @param text line to append, truncated to 27 characters.
            @param center center the text on the screen?
        """

        if center:
            text = text.center(MAX_CHARS_PER_LINE)

        self._text.append(text)


    def appendText(self, text, center = False):
        """
            Appends text to the screen, wraps the text into lines of 27 characters.
        """
        for line in textwrap.wrap(text, MAX_CHARS_PER_LINE):
            self.appendLine(line, center)

    def display(self, clear_screen = True, render_text = True, send_buf = True):
        """
            Converts the Image into something that we can send to g15daemon, then sends it.
        """
        if not self._protocol or getattr(self._protocol, 'activeScreen', None) not in (self, None):
            return

        if clear_screen:
            self._draw.rectangle((0, 0, MAX_X, MAX_Y), fill = 0)

        if render_text:
            y_pos = 0
            for line in self._text:
                self._draw.text((0, y_pos), line, fill = 1)
                y_pos += 8

        if send_buf:
            self._buf = array('B', self._img.getdata())
            G15Screen.display(self)

    @contextmanager
    def context(self, *a, **kw):
        """
            An context manager that sends all the data to g15daemon after it exists...

            with screen.context():
                screen.appendText("Foo")

            # Data sent to g15daemon.

        """
        yield
        self.display(*a, **kw)

import unittest

class G15Screen_Tests(unittest.TestCase):
    def test_blank_screen(self):
        screen = G15Screen()
        self.assertEquals(str(screen), "\x00" * MAX_BUFFER_LENGTH)

    def test_set_pixel(self):
        screen = G15Screen()
        screen.setPixel(0, 0, PIXEL_ON)
        self.assertTrue(str(screen).startswith("\x01"))
        self.assertEqual(screen._buf.count(PIXEL_ON), 1)

        screen.setPixel(159, 42, PIXEL_ON)
        self.assertTrue(str(screen).endswith("\x01"))
        self.assertEqual(screen._buf.count(PIXEL_ON), 2)

        screen.setPixel(159, 42, PIXEL_OFF)
        self.assertEqual(screen._buf.count(PIXEL_ON), 1)


    def test_clear_and_fill(self):
        screen = G15Screen()
        screen.setPixel(55, 25, PIXEL_ON)

        screen.clearScreen()
        self.assertEquals(str(screen), "\x00" * MAX_BUFFER_LENGTH)

        screen.fillScreen()
        self.assertEquals(str(screen), "\x01" * MAX_BUFFER_LENGTH)

    def test_text_screen(self):
        # TODO: More coverage here.
        screen = G15TextScreen()
        with screen.context():
            screen.appendLine("Foo!")



__all__ = ['G15Screen', 'G15TextScreen']