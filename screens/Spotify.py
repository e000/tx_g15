from __future__ import division
from itertools import cycle
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.task import LoopingCall

from tx_g15 import LoopingCallMixin
from tx_g15.g15_screen import G15TextScreen

import dbus
from tx_g15.util.tx_dbus import deferFromDbus


class Spotify(G15TextScreen, LoopingCallMixin):
    def __init__(self, *a, **kw):
        G15TextScreen.__init__(self, *a, **kw)
        LoopingCallMixin.__init__(self, 0.2)

        bus = self.bus = dbus.SessionBus()
        self.spotify = bus.get_object('com.spotify.qt', '/')
        self.lineLen = 0
        self.songDuration = 0
        self.cur_sec = 0
        self.scroll_title = ''
        self._text.extend([''] * 4)
        self.appendLine('                     QUEUE')

        self.altCheckLoopingCall = LoopingCall(self.doChecks)
        self.altCheckLoopingCall.start(1)

    @inlineCallbacks
    def doChecks(self):
        song = yield deferFromDbus(self.spotify.GetMetadata)
        if not len(song):
            self.noSong()
        else:
            oldSongDuration = self.songDuration
            title, artist, self.songDuration = song['xesam:title'], ', '.join(song['xesam:artist']), song['mpris:length'] / 1000000
            if title and artist:
                scroll_title = '%s - %s' % (artist, title)
            elif title:
                scroll_title = '%s' % title
            elif artist:
                scroll_title = '%s' % artist
            else:
                scroll_title = 'Unknown'

            if scroll_title != self.scroll_title:
                self.updateScrollTitle(scroll_title)

            cur_sec = (yield deferFromDbus(self.spotify.Position))
            print cur_sec
            if cur_sec != self.cur_sec or oldSongDuration != self.songDuration:
                self.elapsedChanged(cur_sec)



    def updateScrollTitle(self, scroll_title):
        self.scroll_title = scroll_title
        self.lineLen = len(self.scroll_title)
        if self.lineLen <= 27:
            self._text[1] = self.scroll_title.center(27)
        else:
            self.gen = cycle([0] * 15 + range(self.lineLen - 27) + [self.lineLen - 27] * 15)
            self._text[1] = self.scroll_title[:27]

    def updateScreen(self):
        if self.lineLen > 27:
            i = self.gen.next()
            self._text[1] = self.scroll_title[i:i+27]
            self.clear(clear_text = False)
            self.drawBar(self.cur_sec, self.songDuration)
            self.display(clear_screen = False)

    def elapsedChanged(self, sec):
        with self.context(clear_screen = False):
            self.cur_sec = sec
            self._text[2] = ('%i:%02i/%i:%02i' % (sec//60, sec % 60, self.songDuration / 60, self.songDuration % 60)).center(27)

            self.clear(clear_text = False)
            self.drawBar(self.cur_sec, self.songDuration)

    def drawBar(self, sec, duration):
        d = self._draw.rectangle
        d((5, 26, 155, 32), outline=1)
        if duration > 0 < sec:
            d((6, 27, int(sec/duration*150) + 5, 31), fill=1)

    def noSong(self):
        with self.context(clear_screen = False):
            self.updateScrollTitle("No Song Playing")
            self._text[2] = '0:00/0:00'.center(27)
            self.clear(clear_text= False)
            self.drawBar(0, 0)
