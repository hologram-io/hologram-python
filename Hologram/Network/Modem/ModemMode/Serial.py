# Serial.py - Hologram Python SDK Modem Serial interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

class Serial(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, deviceName = '/dev/ttyUSB0', baudRate = '9600'):
        self.deviceName = deviceName
        self.baudRate = baudRate
        self.localIPAddress = None
        self.remoteIPAddress = None

    def isConnected(self):
        return 0
