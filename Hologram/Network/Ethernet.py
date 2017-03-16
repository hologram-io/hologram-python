from Network import Network
from ..Event import Event
from pythonwifi.iwlibs import Wireless
from pythonwifi.iwlibs import WirelessInfo
import time
import os

class Ethernet(Network):

    def __init__(self, interfaceName = 'eth0'):
        self.interfaceName = interfaceName
        # TODO(zheng): change to ethernet library
        self.ethernet = Wireless(interfaceName)
        super(Ethernet, self).__init__()

    def getBitRate(self):
        bitrate = self.ethernet.wireless_info.getBitrate()
        return "Bit Rate :%s" % self.ethernet.getBitrate()

    def disconnect(self):
        os.system("ifconfig " + self.interfaceName + " down")
        self.event.broadcast('ethernet.disconnected')
        super(Ethernet, self).disconnect()

    def connect(self):
        os.system("ifconfig " + self.interfaceName + " up")
        self.event.broadcast('ethernet.connected')
        super(Ethernet, self).connect()

    def isConnected(self):
        return True

    def getConnectionStatus(self):
        raise Exception('Ethernet mode doesn\'t support this call')

    def getSignalStrength(self):
        raise Exception('Ethernet mode doesn\'t support this call')
