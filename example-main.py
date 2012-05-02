from screens import RhythmBox
from screens import StatsScreen,  ImageTest
from twisted.internet.protocol import ClientCreator
from tx_g15 import ScreenManager
from twisted.internet import reactor

protocol = ScreenManager
screens = [RhythmBox.RhythmBox, ImageTest.GifTest, StatsScreen.StatsScreen, ImageTest.ImageTest]

ClientCreator(reactor, protocol, '/dev/input/event4', screens).connectTCP('localhost', 15550)
reactor.run()