# IPPP.py - Hologram Python SDK Modem PPP interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from ModemMode import ModemMode

class IPPP(ModemMode):

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600',
                 chatscript_file=None):

        super(IPPP, self).__init__(device_name=device_name, baud_rate=baud_rate)

        self.chatscript_file = chatscript_file

        if self.chatscript_file == None:
            raise Exception('Must specify chatscript file')

    @property
    def connect_script(self):
        return '/usr/sbin/chat -v -f ' + self.chatscript_file

    @property
    def chatscript_file(self):
        return self._chatscript_file

    @chatscript_file.setter
    def chatscript_file(self, chatscript_file):
        self._chatscript_file = chatscript_file
