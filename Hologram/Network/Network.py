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

class Network(object):

    def __init__(self):
        self.event = Event()
        self.event.broadcast('network.connected')

    def getConnectionStatus(self):
        return True

    def connect(self):
        self.event.broadcast('network.connected')
        return True

    def disconnect(self):
        self.event.broadcast('network.disconnected')
        return True

    def reconnect(self):
        self.event.broadcast('network.disconnected')
        self.event.broadcast('network.connected')
        return True

    def enforceNetworkPrivileges(self):
        if os.geteuid() != 0:
            raise Exception('You need to have root privileges to use the Wifi interface.'
                            + '\nPlease try again, this time using sudo.')

    @property
    def interfaceName(self):
        return self._interfaceName

    @interfaceName.setter
    def interfaceName(self, name):
        self._interfaceName = name
