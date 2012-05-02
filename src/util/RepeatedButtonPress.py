from twisted.internet import task, reactor

class RepeatedButtonPress:
    """
        A class that will repeat press the button when it is held down.
    """
    def __init__(self, event, callback, delay = .75, frequency = 0.20):
        self.event = event
        self.callback = callback
        self.delay = delay
        self.frequency = frequency
        self.timeout = None
        self.lc = task.LoopingCall(self.callCallback)

    def connect(self, event):
        event.hookEvent(self.event[0], self.keyDown)
        event.hookEvent(self.event[1], self.keyUp)

    def callCallback(self):
        self.callback(self)

    def keyDown(self, event):
        if self.timeout and self.timeout.active():
            self.timeout.cancel()

        self.callCallback()
        self.timeout = reactor.callLater(self.delay, self.startLc)

    def keyUp(self, event):
        if self.timeout and self.timeout.active():
            self.timeout.cancel()
            self.timeout = None
        if self.lc.running:
            self.lc.stop()

    def startLc(self):
        if not self.lc.running:
            self.lc.start(self.frequency)