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

DEFAULT_NETWORK_TIMEOUT = 200

class NetworkManager(object):

    _networkHandlers =  {
        'wifi' : Wifi,
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

    def connect(self, timeout = DEFAULT_NETWORK_TIMEOUT):
        success = self.network.connect(timeout = timeout)
        if success:
            self.networkConnected()
            self.event.broadcast('network.connected')
        return success

    def disconnect(self):
        success = self.network.disconnect()
        if success:
            self.networkDisconnected()
            self.event.broadcast('network.disconnected')
        return success

    def getConnectionStatus(self):
        return self.network.getConnectionStatus()

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
            self.enforceNetworkPrivileges()

            # trim away the 2nd word (e303 in cellular-e303) and pass it into the Cellular constructor
            if network.startswith('cellular'):
                self._network = self._networkHandlers[network](network[9:])
            else:
                self._network = self._networkHandlers[network]()

    def __repr__(self):
        if not self.network:
            return 'Network Agnostic Mode'

        return type(self.network).__name__

    def enforceNetworkPrivileges(self):
        if os.geteuid() != 0:
            raise Exception('You need to have root privileges to use this interface.'
                            + '\nPlease try again, this time using sudo.')

    @property
    def localIPAddress(self):
        return self.network.localIPAddress

    @property
    def remoteIPAddress(self):
        return self.network.remoteIPAddress
