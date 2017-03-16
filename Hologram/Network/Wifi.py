from Network import Network
from ..Event import Event
from pythonwifi.iwlibs import Wireless
from pythonwifi.iwlibs import WirelessInfo
import time
import os

class Wifi(Network):

    def __init__(self, interfaceName = 'wlan0'):
        self.interfaceName = interfaceName
        self.wifi = Wireless(interfaceName)
        super(Wifi, self).__init__()
        self.event.broadcast('wifi.connected')

    def getSSID(self):
        return self.wifi.getEssid()

    def getMode(self):
        return self.wifi.getMode()

    def getWirelessName(self):
        return self.wifi.getWirelessName()

    def getBitRate(self):
        bitrate = self.wifi.wireless_info.getBitrate()
        return "Bit Rate :%s" % self.wifi.getBitrate()

    def getAvgSignalStrength(self):
        mq = self.wifi.getQualityAvg()
        return "quality: " + str(mq.quality) + " signal: " + str(mq.siglevel) \
                + " noise: " + str(mq.nlevel)

    def getMaxSignalStrength(self):
        mq = self.wifi.getQualityMax()
        return "quality: " + str(mq.quality) + " signal: " + str(mq.siglevel) \
                + " noise: " + str(mq.nlevel)

    def disconnect(self):
        os.system("ifconfig " + self.interfaceName + " down")
        self.event.broadcast('wifi.disconnected')
        super(Wifi, self).disconnect()

    def connect(self):
        os.system("ifconfig " + self.interfaceName + " up")
        self.event.broadcast('wifi.connected')
        super(Wifi, self).connect()

    # EFFECTS: Returns the AP address.
    def getAPAddress(self):
        self.disconnect()
        time.sleep(5)
        self.connect()
        return self.wifi.getAPaddr()

    def getConnectionStatus(self):
        raise Exception('WiFi mode doesn\'t support this call yet')

    def setAPAddress(self, ap):
        try:
            self.wifi.setAPaddr(ap)
        except:
            raise Exception('Unable to set AP address to ' + str(ap))

    def isConnected(self):
        return True
