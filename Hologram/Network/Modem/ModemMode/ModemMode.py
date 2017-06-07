# ModemMode.py - Hologram Python SDK modem mode interface
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
from ....Event import Event

class ModemMode(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600', event=Event()):

        # Logging setup.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

        self.event = event
        self.device_name = device_name
        self.baud_rate = baud_rate

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
