# MockPPP.py - Hologram Python SDK Modem PPP mock interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from IPPP import IPPP

class MockPPP(IPPP):

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600',
                 chatscript_file=None):

        super(MockPPP, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                      chatscript_file=chatscript_file)

    @property
    def localIPAddress(self):
        return None

    @property
    def remoteIPAddress(self):
        return None
