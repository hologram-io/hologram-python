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
from logging import NullHandler

class Network(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, event=Event()):
        self.event = event
        # Logging setup.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

    def connect(self):
        self.event.broadcast('network.connected')

    def disconnect(self):
        self.event.broadcast('network.disconnected')

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
