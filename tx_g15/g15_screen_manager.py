from .g15_protocol import G15Protocol, G15Event
from .g15_screen import G15TextScreen
from .g15_screen_mixins import InterruptableScreenMixin, KeyHookMixin
from .util.RepeatedButtonPress import RepeatedButtonPress

class SwitcherScreen(G15TextScreen, InterruptableScreenMixin, KeyHookMixin):
    """
        The window switcher screen. It also holds the splash screen and about page.
    """
    def __init__(self, parent = None):
        G15TextScreen.__init__(self, parent)
        self.hookEvent(G15Event.BUTTON_THREE_UP, self.showAboutScreen)

    def showAboutScreen(self, e):
        with self.context():
            self.clear()
            self.appendLine("About screen goes here.")
        self._protocol.transitionToActiveScreen()

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

    def __init__(self, eventPath = None, screens = None, outHooks = None):
        G15Protocol.__init__(self, eventPath = eventPath, outHooks = outHooks)
        self.switcherScreen = SwitcherScreen(self, )
        self.pauseAndSwitchTo(self.switcherScreen)
        self.transitionDelay = None

        self.screens = screens or []
        self.index = 0

        self._loadScreens()

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

        from twisted.internet import reactor # we have to import reactor here to avoid importing it at startup.
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
            if hasattr(screen, 'init'):
                s.init()
            self.screens.append(s)

    def _hookEvents(self):
        e = self.event
        RepeatedButtonPress(e.BUTTON_ONE, self.switchPrevScreen).connect(e)
        RepeatedButtonPress(e.BUTTON_TWO, self.switchNextScreen).connect(e)

    def connectionInitialized(self):
        self.switcherScreen.showWelcomeScreen()
        self._transitionTo(2, lambda: self.pauseAndSwitchTo(self.screens[self.index]))

    def pauseAndSwitchTo(self, screen):
        if screen is self.activeScreen:
            return
        _as = self.activeScreen
        if hasattr(_as, 'pause'):
            _as.pause()
        self.activeScreen = screen
        if hasattr(screen, 'resume'):
            screen.resume()
        else:
            screen.display()

    def transitionToActiveScreen(self, delay = 2):
        self._transitionTo(delay, self.pauseAndSwitchTo, self.screens[self.index])

    def switchNextScreen(self, e):
        if self.activeScreen is not self.switcherScreen:
            self.pauseAndSwitchTo(self.switcherScreen)
        else:
            self.index = (self.index + 1) % len(self.screens)
        self.switcherScreen.showSwitcherScreen(self.index, self.screens[self.index])
        self.transitionToActiveScreen()

    def switchPrevScreen(self, e):
        if self.activeScreen is not self.switcherScreen:
            self.pauseAndSwitchTo(self.switcherScreen)
        else:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.screens) - 1
        self.switcherScreen.showSwitcherScreen(self.index, self.screens[self.index])
        self.transitionToActiveScreen()


