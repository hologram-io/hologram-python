from ..Event import Event
from Network import Network

class BLE(Network):

    def __init__(self):
        self.event = Event()
        super(BLE, self).__init__()

    def connect(self):
        self.event.broadcast('ble.connected')
        return True

    def disconnect(self):
        self.event.broadcast('ble.disconnected')
        return True

    def getConnectionStatus(self):
        raise Exception('BLE mode doesn\'t support this call yet')

    def reconnect(self):
        return True
