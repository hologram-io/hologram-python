# NetworkManager.py - Hologram Python SDK Network manager interface
#                     This handles the network/connectivity interface for Hologram SDK.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Wifi import Wifi
from Ethernet import Ethernet
from BLE import BLE
from Cellular import Cellular
from Exceptions.HologramError import NetworkError
import logging
from logging import NullHandler
import os

DEFAULT_NETWORK_TIMEOUT = 200

class NetworkManager(object):

    _networkHandlers =  {
        'wifi' : Wifi,
        'cellular': Cellular,
        'ble' : BLE,
        'ethernet' : Ethernet,
    }

    def __init__(self, event, network):

        # Logging setup.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

        self.event = event
        self.networkActive = False
        self.network = network

    # EFFECTS: Event handler function that sets the network disconnect flag.
    def networkDisconnected(self):
        self.networkActive = False

    def networkConnected(self):
        self.networkActive = True

    def listAvailableInterfaces(self):
        return self._networkHandlers.keys()

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, network, modem=None):
        if not network: # non-network mode
            self.networkConnected()
            self._network = None
        elif network not in self._networkHandlers:
            raise NetworkError('Invalid network type: %s' % network)
        else:
            self.__enforce_network_privileges()
            self._network = self._networkHandlers[network](self.event)
        if network == 'cellular':
            if modem is not None:
                self._network.modem = modem
            else:
                try:
                    self._network.autodetect_modem()
                except NetworkError as e:
                    self.logger.info("No modem found. Loading drivers and retrying")
                    self._network.load_modem_drivers()
                    self._network.autodetect_modem()


    def __repr__(self):
        if not self.network:
            return 'Network Agnostic Mode'

        return type(self.network).__name__

    def __enforce_network_privileges(self):

        if os.geteuid() != 0:
            raise RuntimeError('You need to have root privileges to use this interface. Please try again, this time using sudo.')
