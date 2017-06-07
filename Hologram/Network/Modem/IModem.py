# Modem.py - Hologram Python SDK Modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

import logging
from logging import NullHandler
from ...Event import Event

# Modem error codes - this is similar to what we have in Dash system firmware.
MODEM_NO_MATCH = -3
MODEM_ERROR = -2
MODEM_TIMEOUT = -1
MODEM_OK = 0

class IModem(object):

    _error_code_description = {

        MODEM_NO_MATCH: 'Modem response doesn\'t match expected return value',
        MODEM_ERROR: 'Modem error',
        MODEM_TIMEOUT: 'Modem timeout',
        MODEM_OK: 'Modem returned OK'
    }

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600', event=Event()):
        # Logging setup.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

        self.event = event
        self.device_name = device_name

    def __repr__(self):
        return type(self).__name__

    # REQUIRES: A result code (int).
    # EFFECTS: Returns a translated string based on the given modem result code.
    def getResultString(self, result_code):
        if result_code not in self._error_code_description:
            return 'Unknown response code'
        return self._error_code_description[result_code]

    def isConnected(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def connect(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def disconnect(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def enableSMS(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def disableSMS(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def popReceivedSMS(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def localIPAddress(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def remoteIPAddress(self):
        raise NotImplementedError('Must instantiate a Modem type')

    # EFFECTS: Returns the Received Signal Strength Indication (RSSI) value of the modem
    @property
    def signal_strength(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def imsi(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def iccid(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def location(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def operator(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def mode(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def device_name(self):
        return self._device_name

    @device_name.setter
    def device_name(self, device_name):
        self._device_name = device_name
