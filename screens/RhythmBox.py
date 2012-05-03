from __future__ import division
from itertools import cycle

from tx_g15 import LoopingCallMixin
from tx_g15.g15_screen import G15TextScreen

import dbus



class RhythmBox(G15TextScreen, LoopingCallMixin):
    def __init__(self, *a, **kw):
        G15TextScreen.__init__(self, *a, **kw)
        LoopingCallMixin.__init__(self, 0.2)

        self.scroll_title = ''

        bus = self.bus = dbus.SessionBus()
        self.player = dbus.Interface(bus.get_object("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Player"),
            "org.gnome.Rhythmbox.Player")
        self.shell = dbus.Interface(bus.get_object("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Shell"),
            "org.gnome.Rhythmbox.Shell")

        self._text.extend([''] * 4)
        self.appendLine('                     QUEUE')

        add_signal = self.bus.add_signal_receiver
        add_signal(self.elapsedChanged,
            dbus_interface = 'org.gnome.Rhythmbox.Player',
            signal_name = 'elapsedChanged')
        add_signal(self.playingUriChanged,
            dbus_interface = 'org.gnome.Rhythmbox.Player',
            signal_name = 'playingUriChanged')

        self.getStatus()

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

    def playingUriChanged(self, uri):
        if not uri:
            return self.noSong()
        song = self.shell.getSongProperties(uri)
        title, artist, self.songDuration = song['title'], song['artist'], song['duration']
        self._text[0] = 'Now Playing:'.center(27)

        if title and artist:
            scroll_title = '%s - %s' % (artist, title)
        elif title:
            scroll_title = '%s' % title
        elif artist:
            scroll_title = '%s' % artist
        else:
            scroll_title = 'Unknown'

        self.updateScrollTitle(scroll_title)
        self._text[2] = ('0:00/%i:%02i' % (self.songDuration / 60, self.songDuration % 60)).center(27)
        with self.context(clear_screen = False):
            self.clear(clear_text= False)
            self.drawBar(0, self.songDuration)

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
            self._text[1] = ('No Song Playing').center(27)
            self._text[2] = '0:00/0:00'.center(27)
            self.clear(clear_text= False)
            self.drawBar(0, 0)

    def getStatus(self):
        uri = self.player.getPlayingUri()
        self.playingUriChanged(uri)
        if uri:
            elapsed = self.player.getElapsed()
            self.elapsedChanged(elapsed)
