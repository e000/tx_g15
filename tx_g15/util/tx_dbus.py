from twisted.internet.defer import Deferred

def deferFromDbus(f, *a):
    """
        Calls a dbus function asynchronously.

        Returns a deferred that will callback/errback if the proxy function succeeds/fails.

        >>> d = deferFromDbus(interface.MyFunctionCall, 'myArg1')
        >>> d.addCallback(success)

    """
    d = Deferred()
    f.call_async(*a, reply_handler = d.callback, error_handler = d.errback)
    return d