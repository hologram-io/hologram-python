# MockModem.py - Hologram Python SDK mock modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from IModem import IModem

E303_DEVICE_NAME = '/dev/ttyUSB0'
DEFAULT_E303_TIMEOUT = 200

class MockModem(IModem):

    def __init__(self, device_name=E303_DEVICE_NAME, baud_rate='9600',
                 chatscript_file=None):
        super(MockModem, self).__init__(device_name=device_name, baud_rate=baud_rate)

    def _get_attached_devices(self):
        return '/dev/test1, /dev/test2, /dev/ttyACM0'
