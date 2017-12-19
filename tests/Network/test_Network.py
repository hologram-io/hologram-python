# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Network.py - This file implements unit tests for the Network class.

import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network import Network

class TestNetwork(object):

    def test_create_network(self):
        network = Network()

    def test_get_invalid_connection_status(self):
        network = Network()
        with pytest.raises(Exception, message = 'Must instantiate a defined Network type'):
            connectionStatus = network.getConnectionStatus()

    def test_get_invalid_signal_strength(self):
        network = Network()
        with pytest.raises(Exception, message = 'Must instantiate a defined Network type'):
            connectionStatus = network.getSignalStrength()
