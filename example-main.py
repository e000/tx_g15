from screens import RhythmBox
from screens import StatsScreen,  ImageTest
from twisted.internet.protocol import ClientCreator, ServerFactory
from tx_g15 import ScreenManager
from twisted.internet import reactor

protocol = ScreenManager
screens = [RhythmBox.RhythmBox, ImageTest.GifTest, StatsScreen.StatsScreen, ImageTest.ImageTest]

from tx_g15.expiremental.canvas_renderer import RenderOutStream, WebSocketFactory

outhooks = [RenderOutStream.broadcastData]
f = ServerFactory()
f.protocol = RenderOutStream

reactor.listenTCP(9951, WebSocketFactory(f))


ClientCreator(reactor, protocol, '/dev/input/event4', screens, outhooks).connectTCP('localhost', 15550)
reactor.run()