# Network.py - Hologram Python SDK Network interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from ..Event import Event
import os
import logging

class Network(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self):
        self.event = Event()

        # Logging setup.
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        logging.basicConfig(level = logging.INFO)

    def getSignalStrength(self):
        raise NotImplementedError('Must instantiate a defined Network type')

    def connect(self):
        raise NotImplementedError('Must instantiate a defined Network type')

    def disconnect(self):
        raise NotImplementedError('Must instantiate a defined Network type')

    def reconnect(self):
        raise NotImplementedError('Must instantiate a defined Network type')

    def getConnectionStatus(self):
        raise NotImplementedError('Must instantiate a defined Network type')

    @property
    def interfaceName(self):
        return self._interfaceName

    @interfaceName.setter
    def interfaceName(self, name):
        self._interfaceName = name
