from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from .g15_screen import G15Screen
from .g15_event import G15Event

G15_HELLO = "G15 daemon HELLO"
G15_HELLO_LEN = len(G15_HELLO)
G15_PIXBUF_INIT = 'GBUF'

class G15Protocol(Protocol):
    """
        Twisted protocol for talking to g15daemon via sockets.
    """

    def __init__(self, eventPath = None):
        self.helloReceived = False
        self._buffer = ''
        self.event = G15Event()
        self.eventPath = eventPath

    def connectionMade(self):
        """
            Do not use this to callback if a connection has been successfully made,
            this is just twisted saying that a socket connection has been made,
            not that it's successfully gotten G15_HELLO.
        """
        self.transport.setTcpNoDelay(True)

    def connectionInitialized(self):
        """
            This will get called when we have successfully negotiated a connection with
            g15daemon.
        """
        pass

    def dataReceived(self, data):
        self._buffer += data
        if not self.helloReceived:
            if len(self._buffer) >= G15_HELLO_LEN:
                hello, self._buffer = self._buffer[:G15_HELLO_LEN], self._buffer[G15_HELLO_LEN:]
                if hello != G15_HELLO:
                    self.transport.loseConnection(reason = 'Improper HELLO received from g15daemon')
                else:
                    self.helloReceived = True
                    if self.eventPath:
                        reactor.spawnProcess(self.event, 'sudo', ['sudo', 'cat', self.eventPath])
                    else:
                        print "No event path specified, we wont be able to see events."
                    self.transport.write("GBUF")
                    self.connectionInitialized()


        if self._buffer:
            pass # TODO: G15 doesn't send anything back, I think, so do nothing...
             # Do shit

    def sendScreen(self, screen):
        """
            Sends a G15Screen object over the wire.
        """
        assert isinstance(screen, G15Screen)
        if not self.helloReceived:
            raise RuntimeError("We aren't connected yet.")
        print "sending screen %r" % screen
        self.transport.write(str(screen))

