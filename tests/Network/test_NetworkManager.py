# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_NetworkManager.py - This file implements unit tests for the NetworkManager class.

import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network import NetworkManager

class TestNetworkManager():

    def test_create_non_network(self):
        networkManager = NetworkManager.NetworkManager(None, '')
        assert networkManager.networkActive
        assert repr(networkManager) == 'Network Agnostic Mode'

    def test_invalid_create(self):
        with pytest.raises(Exception, match = 'Invalid network type: invalid'):
            networkManager = NetworkManager.NetworkManager(None, 'invalid')

    def test_invalid_ppp_create(self):
        with pytest.raises(Exception, match = 'Invalid network type: invalid-ppp'):
            networkManager = NetworkManager.NetworkManager(None, 'invalid-ppp')

    def test_network_connected(self):
        networkManager = NetworkManager.NetworkManager(None, '')
        networkManager.networkConnected()
        assert networkManager.networkActive

    def test_network_disconnected(self):
        networkManager = NetworkManager.NetworkManager(None, '')
        networkManager.networkDisconnected()
        assert networkManager.networkActive == False
