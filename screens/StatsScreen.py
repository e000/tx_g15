import datetime
import os
import socket
import psutil
from tx_g15.g15_screen import G15TextScreen
from tx_g15.g15_screen_mixins import LoopingCallMixin

class StatsScreen(G15TextScreen, LoopingCallMixin):
    def __init__(self, *a, **kw):
        G15TextScreen.__init__(self, *a, **kw)
        LoopingCallMixin.__init__(self)

        self.appendLine("%s@%s" % (os.getlogin(), socket.gethostname()), center=True)
        for i in xrange(4):
            self.appendLine('')

    def updateScreen(self):
        dt = datetime.datetime.now()
        with self.context():
            self._text[1] = dt.strftime('%A, %b %d, %Y').center(27)
            self._text[2] = dt.strftime('%I:%M:%S %p').center(27)
            self._text[3] = ('CPU:%4.1f%%  RAM:%6.2f%%' % (psutil.cpu_percent(), (psutil.used_phymem()-psutil.cached_phymem())/psutil.TOTAL_PHYMEM*100)).center(27)
            self._text[4] = ('%i processes' % len(psutil.get_pid_list())).center(27)
