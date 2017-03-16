# Cellular.py - Hologram Python SDK Cellular interface
# Author: Hologram <support@hologram.io>
#
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Network import Network
from Modem import E303
from Modem import MS2131
from Modem import IOTA

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
        'iota' : IOTA.IOTA
    }

    def __init__(self, modem):
        self.modem = modem
        self._connectionStatus = CLOUD_DISCONNECTED
        super(Cellular, self).__init__()

    def getConnectionStatus(self):
        return self._connectionStatus

    def connect(self, timeout = DEFAULT_CELLULAR_TIMEOUT):
        self.logger.info('Connecting to cell network with timeout of ' + str(timeout) + ' seconds')
        success = self.modem.connect(timeout = timeout)
        if success:
            self.logger.info('Successfully connected to cell network')
            self._connectionStatus = CLOUD_CONNECTED
            self.event.broadcast('cellular.connected')
        return success

    def disconnect(self):
        self.logger.info('Disconnecting from cell network')
        success = self.modem.disconnect()
        if success:
            self.logger.info('Successfully disconnected from cell network')
            self._connectionStatus = CLOUD_DISCONNECTED
            self.event.broadcast('cellular.disconnected')
        return success

    def reconnect(self):
        self.logger.info('Reconnecting to cell network')
        success = self.disconnect()

        if success == False:
            return False

        return self.connect()

    def getSignalStrength(self):
        raise Exception('Cellular mode doesn\'t support this call yet')

    @property
    def modem(self):
        return self._modem

    @modem.setter
    def modem(self, modem):
        if modem not in self._modemHandlers:
            raise Exception('Invalid modem type: %s' % modem)
        else:
            self._modem = self._modemHandlers[modem]()

    @property
    def localIPAddress(self):
        return self.modem.localIPAddress

    @property
    def remoteIPAddress(self):
        return self.modem.remoteIPAddress
