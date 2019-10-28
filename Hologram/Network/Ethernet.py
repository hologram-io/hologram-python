from Hologram.Network import Network
from Hologram.Event import Event
import time
import os

class Ethernet(Network):

    def __init__(self, interfaceName = 'eth0'):
        self.interfaceName = interfaceName
        # TODO(zheng): change to ethernet library
        # self.ethernet = Wireless(interfaceName)
        super().__init__()

    def getBitRate(self):
        # bitrate = self.ethernet.wireless_info.getBitrate()
        # return "Bit Rate :%s" % self.ethernet.getBitrate()
        return ''

    def disconnect(self):
        os.system("ifconfig " + self.interfaceName + " down")
        self.event.broadcast('ethernet.disconnected')
        super().disconnect()

    def connect(self):
        os.system("ifconfig " + self.interfaceName + " up")
        self.event.broadcast('ethernet.connected')
        super().connect()

    def isConnected(self):
        return True

    def getConnectionStatus(self):
        raise Exception('Ethernet mode doesn\'t support this call')

    def getSignalStrength(self):
        raise Exception('Ethernet mode doesn\'t support this call')

    def getAvgSignalStrength(self):
        raise Exception('Ethernet mode doesn\'t support this call')
