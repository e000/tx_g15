from itertools import cycle
from twisted.internet.defer import inlineCallbacks

from tx_g15 import LoopingCallMixin, G15TextScreen

import dbus
from tx_g15.util.tx_dbus import deferFromDbus


class RhythmBox(G15TextScreen, LoopingCallMixin):
    """
        A screen that shows what's playing on Rhythmbox.
    """
    scrollTitle = ''
    lineLen = 0
    curSec = 0
    songDuration = 0

    def __init__(self, *a, **kw):
        G15TextScreen.__init__(self, *a, **kw)
        LoopingCallMixin.__init__(self, 0.2)

        bus = dbus.SessionBus()
        self.player = dbus.Interface(
            bus.get_object("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Player"),
            "org.gnome.Rhythmbox.Player")
        self.shell = dbus.Interface(
            bus.get_object("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Shell"),
            "org.gnome.Rhythmbox.Shell")

        bus.add_signal_receiver(self.elapsedChanged, 'elapsedChanged', self.player.dbus_interface)
        bus.add_signal_receiver(self.playingUriChanged, 'playingUriChanged', self.player.dbus_interface)

        self._text.extend([''] * 4)
        self.appendLine('                     QUEUE')
        self.getStatus()

    def updateScrollTitle(self, scroll_title):
        """
            Update the scroll title, and set up the scroll generator that scrolls the song when updateScreen is called.
        """
        self.scrollTitle = scroll_title
        self.lineLen = len(self.scrollTitle)

        if self.lineLen > 27:
            self.gen = cycle([0] * 15 + range(self.lineLen - 27) + [self.lineLen - 27] * 15)
            self._text[1] = self.scrollTitle[:27]
        else: # The song will fit on the screen, no need to update.
            self._text[1] = self.scrollTitle.center(27)

    def updateScreen(self):
        """
            Called every .2 seconds, scroll the text of the song if it's too long to fit on the screen.
        """
        if self.lineLen > 27:
            i = self.gen.next()
            self._text[1] = self.scrollTitle[i:i+27]
            self.clear(clear_text = False)
            self.drawBar(self.curSec, self.songDuration)
            self.display(clear_screen = False)

    @staticmethod
    def makeDurationString(sec, full):
        """
            Makes a string in the format of m:ss/m:ss, to show the progress of the song.
        """
        return '%i:%02i/%i:%02i' % (sec / 60, sec % 60, full / 60, full% 60)

    @inlineCallbacks
    def playingUriChanged(self, uri):
        """
            Signal that is fired when the playing song changes in Rhythmbox.
        """
        if not uri:
            self.noSong()
        else:
            song = yield deferFromDbus(self.shell.getSongProperties, uri)
            title, artist, self.songDuration = song['title'], song['artist'], song['duration']
            self._text[0] = 'Now Playing:'.center(27)

            self.updateScrollTitle(
                title and artist and '%s - %s' % (title, artist)
                or title
                or artist
                or 'Unknown'
            )

            self._text[2] = self.makeDurationString(0, self.songDuration).center(27)
            with self.context(clear_screen = False):
                self.clear(clear_text= False)
                self.drawBar(0, self.songDuration)


    def elapsedChanged(self, sec):
        """
            Signal that is fired when the position of the song changes.
        """
        with self.context(clear_screen = False):
            self.curSec = sec
            self._text[2] = self.makeDurationString(sec, self.songDuration).center(27)

            self.clear(clear_text = False)
            self.drawBar(self.curSec, self.songDuration)

    def drawBar(self, sec, duration):
        """
            Draw a rectangle on the screen representing where the song is at.
        """
        d = self._draw.rectangle
        d((5, 26, 155, 32), outline=1)
        if duration > 0 < sec:
            d((6, 27, int(sec/(duration*150.0)) + 5, 31), fill=1)

    def noSong(self):
        """
            Called when no song is playing.
        """
        with self.context(clear_screen = False):
            self._text[1] = ('No Song Playing').center(27)
            self._text[2] = self.makeDurationString(0, 0).center(27)
            self.clear(clear_text= False)
            self.drawBar(0, 0)

    @inlineCallbacks
    def getStatus(self):
        """
            Get the current playing song and update the screen.
        """
        uri = yield deferFromDbus(self.player.getPlayingUri)
        yield self.playingUriChanged(uri)
        if uri:
            elapsed = yield deferFromDbus(self.player.getElapsed)
            self.elapsedChanged(elapsed)
