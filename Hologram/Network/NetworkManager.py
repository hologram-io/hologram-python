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
import os
import sys

DEFAULT_NETWORK_TIMEOUT = 200

class NetworkManager(object):

    _networkHandlers =  {
        'wifi' : Wifi,
        'cellular': Cellular,
        'cellular-ms2131': Cellular,
        'cellular-e303': Cellular,
        'cellular-iota': Cellular,
        'ble' : BLE,
        'ethernet' : Ethernet,
        }

    def __init__(self, event, network):
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
    def network(self, network):
        if not network: # non-network mode
            self.networkConnected()
            self._network = None
        elif network not in self._networkHandlers:
            raise Exception('Invalid network type: %s' % network)
        else:
            self.__enforce_network_privileges()

            # trim away the 2nd word (e303 in cellular-e303) and pass it into the Cellular constructor
            if network.startswith('cellular'):
                self._network = self._networkHandlers[network](network[9:], self.event)
            else:
                self._network = self._networkHandlers[network](self.event)

    def __repr__(self):
        if not self.network:
            return 'Network Agnostic Mode'

        return type(self.network).__name__

    def __enforce_network_privileges(self):

        try:
            if os.geteuid() != 0:
                raise RuntimeError
        except RuntimeError  as e:
            sys.exit('You need to have root privileges to use this interface.' \
                   + '\nPlease try again, this time using sudo.')

