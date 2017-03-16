# IOTA.py - Hologram Python SDK IOTA modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Modem import Modem

IOTA_DEVICE_NAME = '/dev/ttyACM0'

DEFAULT_IOTA_TIMEOUT = 200

class IOTA(Modem):

    def __init__(self, mode = 'ppp', deviceName = IOTA_DEVICE_NAME, baudRate = '9600',
                 chatScriptFile = '../../example-script'):

        super(IOTA, self).__init__(mode = mode, deviceName = deviceName,
                                   baudRate = baudRate, chatScriptFile = chatScriptFile)
        self.logger.info('Instantiated an iota interface with device name of ' + deviceName)

    def isConnected(self):
        return self._mode.connected()

    def connect(self, timeout = DEFAULT_IOTA_TIMEOUT):
        return self._mode.connect(timeout = timeout)

    def disconnect(self):
        return self._mode.disconnect()
