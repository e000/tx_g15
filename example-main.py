from twisted.internet.protocol import ClientCreator
from screens import StatsScreen,  ImageTest
from tx_g15.g15_screen_manager import ScreenManager
from twisted.internet import reactor

protocol = ScreenManager
screens = [ImageTest.GifTest, StatsScreen.StatsScreen, ImageTest.ImageTest]

ClientCreator(reactor, protocol, '/dev/input/event4', screens).connectTCP('localhost', 15550)
reactor.run()