# IPPP.py - Hologram Python SDK Modem PPP interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import logging
from logging import NullHandler
from Hologram.Event import Event

class IPPP:

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600',
                 chatscript_file=None, event=Event()):

        # Logging setup.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

        self.event = event
        self.device_name = device_name
        self.baud_rate = baud_rate

        self.chatscript_file = chatscript_file

        if self.chatscript_file is None:
            raise Exception('Must specify chatscript file')

    @property
    def device_name(self):
        return self._device_name

    @device_name.setter
    def device_name(self, device_name):
        self._device_name = device_name

    @property
    def baud_rate(self):
        return self._baud_rate

    @baud_rate.setter
    def baud_rate(self, baud_rate):
        self._baud_rate = baud_rate
        
    @property
    def connect_script(self):
        return '/usr/sbin/chat -v -f ' + self.chatscript_file

    @property
    def chatscript_file(self):
        return self._chatscript_file

    @chatscript_file.setter
    def chatscript_file(self, chatscript_file):
        self._chatscript_file = chatscript_file
