from twisted.internet import glib2reactor
glib2reactor.install()
import dbus
import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop (set_as_default = True)

from screens import RhythmBox, Spotify
from screens import StatsScreen,  ImageTest
from twisted.internet.protocol import ClientCreator, ServerFactory
from tx_g15 import ScreenManager
from twisted.internet import reactor

protocol = ScreenManager
#screens = [RhythmBox.RhythmBox, ImageTest.GifTest, StatsScreen.StatsScreen, ImageTest.ImageTest]
screens = [Spotify.Spotify]

from tx_g15.expiremental.canvas_renderer import RenderOutStream, WebSocketFactory

outhooks = [RenderOutStream.broadcastData]
f = ServerFactory()
f.protocol = RenderOutStream

reactor.listenTCP(9951, WebSocketFactory(f))


ClientCreator(reactor, protocol, '/dev/input/event4', screens, outhooks).connectTCP('localhost', 15550)
reactor.run()