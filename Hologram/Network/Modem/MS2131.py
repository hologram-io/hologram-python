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

    def __init__(self, device_name=MS2131_DEVICE_NAME, baud_rate='9600',
                 chatscript_file=None):

        super(MS2131, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                     chatscript_file=chatscript_file)

    def isConnected(self):
        return self._mode.connected()

    def connect(self, timeout = DEFAULT_MS2131_TIMEOUT):
        self._enforce_modem_attached()
        return self._mode.connect(timeout = timeout)

    def disconnect(self):
        self._enforce_modem_attached()
        return self._mode.disconnect()

    # EFFECTS: Returns True if a MS2131 modem is physically attached to the machine.
    def isModemAttached(self):
        dev_devices = self._get_attached_devices()
        return MS2131_DEVICE_NAME in dev_devices
