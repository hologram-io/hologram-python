from ..Event import Event
from Network import Network

class BLE(Network):

    def __init__(self):
        self.event = Event()
        super(BLE, self).__init__()

    def getConnectionStatus(self):
        return True

    def connect(self):
        self.event.broadcast('ble.connected')
        return True

    def disconnect(self):
        self.event.broadcast('ble.disconnected')
        return True

    def reconnect(self):
        return True
