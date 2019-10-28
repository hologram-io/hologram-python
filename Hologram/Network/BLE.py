from Hologram.Event import Event
from Hologram.Network import Network

class BLE(Network):

    def __init__(self):
        self.event = Event()
        super().__init__()

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
