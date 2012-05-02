from struct import Struct
from twisted.internet.protocol import ProcessProtocol

class G15Event(ProcessProtocol):
    """
        Handles keyboard events from G buttons.
    """

    CIRCLE_DOWN = (189, 1)
    CIRCLE_UP = (189, 0)
    CIRCLE = CIRCLE_DOWN, CIRCLE_UP

    BUTTON_ONE_DOWN = (190, 1)
    BUTTON_ONE_UP = (190, 0)
    BUTTON_ONE = BUTTON_ONE_DOWN, BUTTON_ONE_UP

    BUTTON_TWO_DOWN = (191, 1)
    BUTTON_TWO_UP = (191, 0)
    BUTTON_TWO = BUTTON_TWO_DOWN, BUTTON_TWO_UP

    BUTTON_THREE_DOWN = (192, 1)
    BUTTON_THREE_UP = (192, 0)
    BUTTON_THREE = BUTTON_THREE_DOWN, BUTTON_THREE_UP

    BUTTON_FOUR_DOWN = (193, 1)
    BUTTON_FOUR_UP = (193, 0)
    BUTTON_FOUR = BUTTON_FOUR_DOWN, BUTTON_FOUR_UP


    G1_DOWN = (167, 1)
    G1_UP = (167, 0)
    G1 = G1_DOWN, G1_UP

    G2_DOWN = (168, 1)
    G2_UP = (168, 0)
    G2 = G1_DOWN, G2_UP

    G3_DOWN = (169, 1)
    G3_UP = (169, 0)
    G3 = G3_DOWN, G3_UP

    G4_DOWN = (170, 1)
    G4_UP = (170, 0)
    G4 = G4_DOWN, G4_UP

    G5_DOWN = (171, 1)
    G5_UP = (171, 0)
    G5 = G5_DOWN, G5_UP

    G6_DOWN = (172, 1)
    G6_UP = (172, 0)
    G6 = G6_DOWN, G6_UP

    def __init__(self):
        self.hooks = {}
        self._buf = ''
        self.struct = Struct('llHHi')
        self.unpack = self.struct.unpack

    def outReceived(self, recd):
        self._buf += recd
        while len(self._buf) >= 16:
            data, self._buf = self._buf[:16], self._buf[16:]
            self.eventReceived(self.unpack(data))

    def eventReceived(self, data):
        times, timeu, code, key, value = data
        event = (key, value)
        if event in self.hooks:
            for cb in self.hooks[event]:
                cb(event)

    def hookEvent(self, event, cb):
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(cb)

    def unhookEvent(self, event, cb):
        if event not in self.hooks:
            return
        while cb in self.hooks[event]:
            self.hooks[event].remove(cb)
        if not len(self.hooks[event]):
            del self.hooks[event]