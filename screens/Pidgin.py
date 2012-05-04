import re
import dbus
from twisted.internet.defer import inlineCallbacks
from tx_g15.g15_screen import G15TextScreen
from tx_g15.util.misc import squeeze, truncate
from tx_g15.util.tx_dbus import deferFromDbus

class Pidgin(G15TextScreen):
    """
        A screen that updates when buddies sign on / off, or if an IM is received.
    """
    def __init__(self, parent = None):
        G15TextScreen.__init__(self, parent)

        bus = dbus.SessionBus()
        self.pidgin = dbus.Interface(
            bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject"),
            "im.pidgin.purple.PurpleInterface"
        )

        self.appendText("Pidgin Screen Loaded. Waiting for events.", center = True)

        bus.add_signal_receiver(self.buddySignedOn, 'BuddySignedOn', self.pidgin.dbus_interface)
        bus.add_signal_receiver(self.buddySignedOff, 'BuddySignedOff', self.pidgin.dbus_interface)
        bus.add_signal_receiver(self.receivedImMessage, 'ReceivedImMsg', self.pidgin.dbus_interface)

    @inlineCallbacks
    def buddySignedOn(self, e):
        name = yield deferFromDbus(self.pidgin.PurpleBuddyGetAlias, e)
        with self.context():
            self.appendLine("online: %s" % name, center = True)

    @inlineCallbacks
    def buddySignedOff(self, e):
        name = yield deferFromDbus(self.pidgin.PurpleBuddyGetAlias, e)
        with self.context():
            self.appendLine("offline: %s" % name, center = True)

    def receivedImMessage(self, _, who, message, time, __):
        with self.context():
            self.appendText(truncate("%s: %s" % (who, squeeze(re.sub(r'<[^>]*?>', '', message))), min_pos = 27, max_pos = 27 * 2))

