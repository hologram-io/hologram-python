
class HologramError(Exception):
    def __repr__(self):
        return '%s: %s' % (type(self).__name__, str(self))

class AuthenticationError(HologramError):
    pass

class PPPError(HologramError):
    pass

class PPPConnectionError(PPPError):

    _PPPD_RETURNCODES = {
        1:  'Fatal error occured',
        2:  'Error processing options',
        3:  'Not executed as root or setuid-root',
        4:  'No kernel support, PPP kernel driver not loaded',
        5:  'Received SIGINT, SIGTERM or SIGHUP',
        6:  'Modem could not be locked',
        7:  'Modem could not be opened',
        8:  'Connect script failed',
        9:  'pty argument command could not be run',
        10: 'PPP negotiation failed',
        11: 'Peer failed (or refused) to authenticate',
        12: 'The link was terminated because it was idle',
        13: 'The link was terminated because the connection time limit was reached',
        14: 'Callback negotiated',
        15: 'The link was terminated because the peer was not responding to echo requests',
        16: 'The link was terminated by the modem hanging up',
        17: 'PPP negotiation failed because serial loopback was detected',
        18: 'Init script failed',
        19: 'Failed to authenticate to the peer',
    }

    def __init__(self, code, output=None):
        self.code = code
        self.message = self._PPPD_RETURNCODES.get(code, 'Undocumented error occured')
        self.output = output

        super(PPPConnectionError, self).__init__(code, output)

class SerialError(HologramError):
    pass
