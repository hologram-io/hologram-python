# PPP.py - Hologram Python SDK Modem PPP interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from pppd import PPPConnection

DEFAULT_PPP_TIMEOUT = 200

class PPP(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, deviceName = '/dev/ttyUSB0', baudRate = '9600',
                 chatScriptFile = '../../example-script'):

        self.deviceName = deviceName
        self.baudRate = baudRate
        self.chatScriptFile = chatScriptFile

        self.connectScript = '/usr/sbin/chat -v -f ' + self.chatScriptFile

        self.ppp = PPPConnection(self.deviceName, self.baudRate, 'noipdefault',
                                 'usepeerdns', 'defaultroute', 'persist', 'noauth',
                                 connect = self.connectScript)

    def isConnected(self):
        return self.ppp.connected()

    def connect(self, timeout = DEFAULT_PPP_TIMEOUT):
        return self.ppp.connect(timeout = timeout)

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
