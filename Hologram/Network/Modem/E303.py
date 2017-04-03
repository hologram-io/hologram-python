# E303.py - Hologram Python SDK Huawei E303 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Modem import Modem

E303_DEVICE_NAME = '/dev/ttyUSB0'
DEFAULT_E303_TIMEOUT = 200

class E303(Modem):

    def __init__(self, mode = 'ppp', deviceName = E303_DEVICE_NAME, baudRate = '9600',
                 chatScriptFile = None):

        super(E303, self).__init__(mode = mode, deviceName = deviceName,
                                   baudRate = baudRate, chatScriptFile = chatScriptFile)
        self.logger.info('Instantiated an E303 interface with device name of ' + deviceName)

    def isConnected(self):
        return self._mode.connected()

    def connect(self, timeout = DEFAULT_E303_TIMEOUT):
        return self._mode.connect(timeout = timeout)

    def disconnect(self):
        return self._mode.disconnect()
