from twisted.internet import reactor
from .g15_protocol import G15Protocol
from .g15_screen import G15TextScreen
from .g15_screen_mixins import InterruptableScreenMixin
from .util.RepeatedButtonPress import RepeatedButtonPress

class SwitcherScreen(G15TextScreen, InterruptableScreenMixin):
    """
        The window switcher screen. It also holds the splash screen and about page.
    """
    def showWelcomeScreen(self):
        with self.context():
            self.appendLine('')
            self.appendLine(self._protocol.applicationName, center = True)
            self.appendLine("by %s" % self._protocol.authorName, center = True)
            self.appendLine('')
            self.appendLine(' PREV   NEXT  ABOUT')

    def showSwitcherScreen(self, index, screen):
        with self.context():
            w = self.appendLine
            w('')
            w('<=[Screen %i]=>' % (index + 1), center=True)
            w('[%s]' % screen.__class__.__name__, center=True)
            w('')
            w(' PREV   NEXT  ABOUT')


class ScreenManager(G15Protocol):
    """
        A screen manager that lets you write many screen "Modules" that can run concurrently and
        allows you to switch between them, only allowing one to draw at once.
    """
    applicationName = "None"
    authorName = "None"
    activeScreen = None

    def __init__(self, eventPath = None, screens = None):
        G15Protocol.__init__(self, eventPath = eventPath)
        self.switcherScreen = SwitcherScreen(self, )
        self.pauseAndSwitchTo(self.switcherScreen)
        self.transitionDelay = None

        self.screens = screens or []
        self.index = 0

    def sendScreen(self, screen):
        if screen is not self.activeScreen or not self.helloReceived:
            return
        G15Protocol.sendScreen(self, screen)

    def _transitionTo(self, delay, f, *a, **kw):
        if self.transitionDelay:
            self.transitionDelay.cancel()

        def callback():
            self.transitionDelay = None
            print "Calling", f
            f(*a, **kw)

        self.transitionDelay = reactor.callLater(delay, callback)

    def addScreen(self, screenClass):
        self.screens.append(screenClass)

    def _loadScreens(self):
        self._hookEvents()
        screens = self.screens[:]
        print screens
        self.screens[:] = []
        for screen in screens:
            s = screen(self)
            s.init()
            self.screens.append(s)

        self.pauseAndSwitchTo(self.screens[self.index])

    def _hookEvents(self):
        e = self.event
        RepeatedButtonPress(e.BUTTON_ONE, self.switchPrevScreen).connect(e)
        RepeatedButtonPress(e.BUTTON_TWO, self.switchNextScreen).connect(e)

    def connectionInitialized(self):
        self.switcherScreen.showWelcomeScreen()
        self._transitionTo(2, self._loadScreens)

    def pauseAndSwitchTo(self, screen):
        _as = self.activeScreen
        if hasattr(_as, 'pause'):
            _as.pause()
        self.activeScreen = screen
        if hasattr(screen, 'resume'):
            screen.resume()
        else:
            screen.display()

    def switchNextScreen(self, e):
        self.index = (self.index + 1) % len(self.screens)
        self.pauseAndSwitchTo(self.switcherScreen)
        self.switcherScreen.showSwitcherScreen(self.index, self.screens[self.index])
        self._transitionTo(2, self.pauseAndSwitchTo, self.screens[self.index])

    def switchPrevScreen(self, e):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.screens) - 1
        self.pauseAndSwitchTo(self.switcherScreen)
        self.switcherScreen.showSwitcherScreen(self.index, self.screens[self.index])
        self._transitionTo(2, self.pauseAndSwitchTo, self.screens[self.index])

