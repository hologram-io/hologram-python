# MS2131.py - Hologram Python SDK Huawei MS2131 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Modem import Modem

MS2131_DEVICE_NAME = '/dev/ttyUSB0'
DEFAULT_MS2131_TIMEOUT = 200

class MS2131(Modem):

    def __init__(self, mode = 'ppp', deviceName = MS2131_DEVICE_NAME, baudRate = '9600',
                 chatScriptFile = '../../example-script'):

        super(MS2131, self).__init__(mode = mode, deviceName = deviceName,
                                     baudRate = baudRate, chatScriptFile = chatScriptFile)
        self.logger.info('Instantiated a MS2131 interface with device name of ' + deviceName)

    def isConnected(self):
        return self._mode.connected()

    def connect(self, timeout = DEFAULT_MS2131_TIMEOUT):
        return self._mode.connect(timeout = timeout)

    def disconnect(self):
        return self._mode.disconnect()
