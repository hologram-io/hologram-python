# Cellular.py - Hologram Python SDK Cellular interface
# Author: Hologram <support@hologram.io>
#
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from ..Event import Event
from Modem import Modem
from Modem import E303
from Modem import IOTA
from Modem import MS2131
from Network import Network
import subprocess

# Cellular return codes.
CLOUD_DISCONNECTED = 0
CLOUD_CONNECTED = 1
CLOUD_ERR_SIM = 3
CLOUD_ERR_SIGNAL = 5
CLOUD_ERR_CONNECT = 12

DEFAULT_CELLULAR_TIMEOUT = 200 # slightly more than 3 mins

class Cellular(Network):

    _modemHandlers = {
        'e303': E303.E303,
        'ms2131': MS2131.MS2131,
        'iota' : IOTA.IOTA,
        '': Modem
    }

    def __init__(self, modem='', event=Event()):
        super(Cellular, self).__init__(event=event)
        self._connectionStatus = CLOUD_DISCONNECTED
        self.modem = modem

    def getConnectionStatus(self):
        return self._connectionStatus

    def connect(self, timeout = DEFAULT_CELLULAR_TIMEOUT):
        self.logger.info('Connecting to cell network with timeout of ' + str(timeout) + ' seconds')
        self._enforce_modem_attached()
        success = self.modem.connect(timeout = timeout)
        if success:
            self.logger.info('Successfully connected to cell network')
            self._connectionStatus = CLOUD_CONNECTED
            self.event.broadcast('cellular.connected')
            super(Cellular, self).connect()
        else:
            self.logger.info('Failed to connect to cell network')

        return success

    def disconnect(self):
        self.logger.info('Disconnecting from cell network')
        self._enforce_modem_attached()
        success = self.modem.disconnect()
        if success:
            self.logger.info('Successfully disconnected from cell network')
            self._connectionStatus = CLOUD_DISCONNECTED
            self.event.broadcast('cellular.disconnected')
            super(Cellular, self).connect()
        else:
            self.logger.info('Failed to disconnect from cell network')

        return success

    def reconnect(self):
        self.logger.info('Reconnecting to cell network')
        success = self.disconnect()

        if success == False:
            self.logger.info('Failed to disconnect from cell network')
            return False

        return self.connect()

    def enableSMS(self):
        return self.modem.enableSMS()

    def disableSMS(self):
        return self.modem.disableSMS()

    def popReceivedSMS(self):
        return self.modem.popReceivedSMS()

    # EFFECTS: Returns a list of devices that are physically attached and recognized
    #          by the machine.
    def _get_attached_devices(self):
        return subprocess.check_output('ls /dev/tty*', stderr=subprocess.STDOUT,
                                       shell=True)
    def _get_active_device_name(self):

        self._enforce_modem_attached()

        dev_devices = self._get_attached_devices()
        if '/dev/ttyACM0' in dev_devices:
            self.logger.info('/dev/ttyACM0 found to be active modem interface')
            return 'iota'
        elif '/dev/ttyUSB0' in dev_devices:
            self.logger.info('/dev/ttyUSB0 found to be active modem interface')
            return 'ms2131'
        else:
            raise Exception('Modem device name not found')

    def _enforce_modem_attached(self):
        if self.isModemAttached() == False:
            raise Exception('Modem is not physically connected')

    # EFFECTS: Returns True if a supported modem is physically attached to the machine.
    def isModemAttached(self):
        dev_devices = self._get_attached_devices()
        return ('/dev/ttyACM0' in dev_devices) or ('/dev/ttyUSB0' in dev_devices)

    @property
    def modem(self):
        return self._modem

    @modem.setter
    def modem(self, modem):
        modem = self._get_active_device_name()
        if modem not in self._modemHandlers:
            raise Exception('Invalid modem type: %s' % modem)
        else:
            self._modem = self._modemHandlers[modem](event=self.event)

    @property
    def localIPAddress(self):
        return self.modem.localIPAddress

    @property
    def remoteIPAddress(self):
        return self.modem.remoteIPAddress

    @property
    def signal_strength(self):
        return self.modem.signal_strength

    @property
    def imsi(self):
        return self.modem.imsi

    @property
    def iccid(self):
        return self.modem.iccid

    @property
    def operator(self):
        return self.modem.operator

    # This property will be set to None if a modem is not physically attached.
    @property
    def active_modem_interface(self):
        return repr(self.modem)

    @property
    def location(self):
        return self.modem.location
