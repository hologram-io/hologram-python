
class HologramError(Exception):
    def __repr__(self):
        return '%s: %s' % (type(self).__name__, str(self))

class AuthenticationError(HologramError):
    pass

class PPPError(HologramError):
    pass

class SerialError(HologramError):
    pass
