import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network import Ethernet

class TestEthernet(object):

    def test_Ethernet(self):
        ethernet = Ethernet.Ethernet()
        assert ethernet.interfaceName == 'eth0'

        ethernet.interfaceName = 'eth1'
        assert ethernet.interfaceName == 'eth1'

    def test_Ethernet_with_specified_interface(self):

        ethernet = Ethernet.Ethernet(interfaceName = 'eth2')
        assert ethernet.interfaceName == 'eth2'

    def test_get_invalid_signal_strength(self):
        ethernet = Ethernet.Ethernet()
        with pytest.raises(Exception, message = 'Ethernet mode doesn\'t support this call'):
            connectionStatus = network.getAvgSignalStrength()
