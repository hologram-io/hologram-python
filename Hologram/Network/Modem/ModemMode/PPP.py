# PPP.py - Hologram Python SDK Modem PPP interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import subprocess
from pppd import PPPConnection

DEFAULT_PPP_TIMEOUT = 200

class PPP(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, deviceName = '/dev/ttyUSB0', baudRate = '9600',
                 chatScriptFile = None):

        self.deviceName = deviceName
        self.baudRate = baudRate
        self.chatScriptFile = chatScriptFile

        if self.chatScriptFile == None:
            raise Exception('Must specify chatscript file')

        self.connectScript = '/usr/sbin/chat -v -f ' + self.chatScriptFile

        self.ppp = PPPConnection(self.deviceName, self.baudRate, 'noipdefault',
                                 'usepeerdns', 'defaultroute', 'persist', 'noauth',
                                 connect = self.connectScript)

    def isConnected(self):
        return self.ppp.connected()

    def connect(self, timeout = DEFAULT_PPP_TIMEOUT):
        result = self.ppp.connect(timeout = timeout)

        if result == True:
            subprocess.call('ip route add 10.176.0.0/16 dev ppp0', shell=True)
            subprocess.call('ip route add 10.254.0.0/16 dev ppp0', shell=True)
            subprocess.call('ip route add default dev ppp0', shell=True)
        return result

    def disconnect(self):
        return self.ppp.disconnect()

    @property
    def deviceName(self):
        return self._deviceName

    @deviceName.setter
    def deviceName(self, deviceName):
        self._deviceName = deviceName

    @property
    def baudRate(self):
        return self._baudRate

    @baudRate.setter
    def baudRate(self, baudRate):
        self._baudRate = baudRate

    @property
    def localIPAddress(self):
        return self.ppp.raddr

    @property
    def remoteIPAddress(self):
        return self.ppp.laddr
