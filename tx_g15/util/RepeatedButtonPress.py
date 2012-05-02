from twisted.internet import task, reactor

class RepeatedButtonPress:
    """
        A class that will repeat press the button when it is held down.
    """
    def __init__(self, event, callback, delay = .75, frequency = 0.20):
        self._event = event
        self._callback = callback
        self._delay = delay
        self._frequency = frequency
        self._timeoutDelay = None
        self._loopingCall = task.LoopingCall(self.callCallback)

    def connect(self, event):
        event.hookEvent(self._event[0], self._on_keyDown)
        event.hookEvent(self._event[1], self._on_KeyUp)

    def callCallback(self):
        self._callback(self)

    def _on_keyDown(self, event):
        if self._timeoutDelay and self._timeoutDelay.active():
            self._timeoutDelay.cancel()

        self.callCallback()
        self._timeoutDelay = reactor.callLater(self._delay, self._startLoopingCall)

    def _on_KeyUp(self, event):
        if self._timeoutDelay and self._timeoutDelay.active():
            self._timeoutDelay.cancel()
            self._timeoutDelay = None
        if self._loopingCall.running:
            self._loopingCall.stop()

    def _startLoopingCall(self):
        if not self._loopingCall.running:
            self._loopingCall.start(self._frequency)