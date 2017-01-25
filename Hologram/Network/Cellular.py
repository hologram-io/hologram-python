from ..Event import Event
from Network import Network

class Cellular(Network):

    def __init__(self):
        self.event = Event()
        super(Cellular, self).__init__()

    def getConnectionStatus(self):
        return True

    def connect(self):
        self.event.broadcast('cellular.connected')
        return True

    def disconnect(self):
        self.event.broadcast('cellular.disconnected')
        return True

    def reconnect(self):
        return True
