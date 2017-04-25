# Modem.py - Hologram Python SDK Modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

import logging
import os
import subprocess

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

    _device_name_to_modem_map = {
        '/dev/ttyUSB0': 'ms2131', #e303 as well (this needs to be fixed)
        '/dev/ttyACM0': 'iota'
    }

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600'):
        self.logger = logging.getLogger(type(self).__name__)
        self.device_name = device_name

    def __repr__(self):
        return type(self).__name__

    # REQUIRES: A result code (int).
    # EFFECTS: Returns a translated string based on the given modem result code.
    def getResultString(self, result_code):
        if result_code not in self._error_code_description:
            return 'Unknown response code'
        return self._error_code_description[result_code]

    # EFFECTS: Returns True if a supported modem is physically attached to the machine.
    def isModemAttached(self):
        dev_devices = self._get_attached_devices()
        return ('/dev/ttyACM0' in dev_devices) or ('/dev/ttyUSB0' in dev_devices)

    def _enforce_modem_attached(self):
        if self.isModemAttached() == False:
            raise Exception('Modem is not physically connected')

    def isConnected(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def connect(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def disconnect(self):
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
    def cell_locate(self):
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

    # This property will be set to None if a modem is not physically attached.
    @property
    def active_modem_interface(self):
        if self.isModemAttached() == False:
            return None

        dev_devices = self._get_attached_devices()
        if '/dev/ttyACM0' in dev_devices:
            self.logger.info('/dev/ttyACM0 found to be active modem interface')
            self.device_name = '/dev/ttyACM0'
        elif '/dev/ttyUSB0' in dev_devices:
            self.logger.info('/dev/ttyUSB0 found to be active modem interface')
            self.device_name = '/dev/ttyUSB0'
        else:
            raise Exception('Modem device name not found')

        return self._device_name_to_modem_map[self.device_name]

    # EFFECTS: Returns a list of devices that are physically attached and recognized
    #          by the machine.
    def _get_attached_devices(self):
        return subprocess.check_output('ls /dev/tty*', stderr=subprocess.STDOUT,
                                       shell=True)
