# Modem.py - Hologram Python SDK Modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
from ModemMode import PPP
from ModemMode import Serial
import logging

class Modem(object):

    _modeHandlers = {
        'ppp': PPP,
        'serial': Serial,
    }

    def __init__(self, mode = 'ppp', deviceName = '/dev/ttyUSB0', baudRate = '9600',
                 chatScriptFile = '../../example-script'):

        self._mode = None
        if mode == 'ppp':
            self._mode = PPP(deviceName = deviceName, baudRate = baudRate,
                               chatScriptFile = chatScriptFile)
        else:
            self._mode = Serial()

        # Logging setup.
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        logging.basicConfig(level = logging.INFO)

    def __repr__(self):
        return type(self).__name__

    def isConnected(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def connect(self):
        raise NotImplementedError('Must instantiate a Modem type')

    def disconnect(self):
        raise NotImplementedError('Must instantiate a Modem type')

    @property
    def localIPAddress(self):
        return self._mode.localIPAddress

    @property
    def remoteIPAddress(self):
        return self._mode.remoteIPAddress

    @property
    def mode(self):
        return self._mode
