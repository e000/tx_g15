class InterruptableScreenMixin:
    """
        A mixin that allows the screen to be paused and resumed when shifting from active -> inactive and back.
    """
    paused = True
    def pause(self):
        if not self.paused:
            self.paused = True
            self.onPause()

    def resume(self):
        if self.paused:
            self.paused = False
            self.onResume()
            self.display()
        self.paused = False
        pass

    def init(self):
        pass

    def onResume(self):
        pass

    def onPause(self):
        pass

class LoopingCallMixin(InterruptableScreenMixin):
    """
        A mixin that calls updateScreen on a regular interval when the screen is active.
    """
    def __init__(self, updateFrequency = 1):
        from twisted.internet import task
        self._loopingCall = task.LoopingCall(self.updateScreen)
        self._loopingCall.updateFrequency = 1

    def updateScreen(self):
        pass

    def onPause(self):
        if self._loopingCall.running:
            self._loopingCall.stop()

    def onResume(self):
        if not self._loopingCall.running:
            self._loopingCall.start(self._loopingCall.updateFrequency)

class KeyHookMixin():
    # TODO: Write me!

    pass
