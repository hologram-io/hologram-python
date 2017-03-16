import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network import NetworkManager

class TestNetworkManager(object):

    def test_create_non_network(self):
        networkManager = NetworkManager.NetworkManager(None, '')
        assert networkManager.networkActive == True
        assert repr(networkManager) == 'Network Agnostic Mode'

    def test_create_iota(self):
        networkManager = NetworkManager.NetworkManager(None, 'cellular-iota')
        assert networkManager.networkActive == False
        assert repr(networkManager) == 'Cellular'
        assert repr(networkManager.network.modem) == 'IOTA'

    def test_create_e303(self):
        networkManager = NetworkManager.NetworkManager(None, 'cellular-e303')
        assert networkManager.networkActive == False
        assert repr(networkManager) == 'Cellular'
        assert repr(networkManager.network.modem) == 'E303'

    def test_create_ethernet(self):
        networkManager = NetworkManager.NetworkManager(None, 'ethernet')
        assert networkManager.networkActive == False
        assert repr(networkManager) == 'Ethernet'

    def test_invalid_create(self):
        with pytest.raises(Exception, message = 'Invalid network type: invalid'):
            networkManager = NetworkManager.NetworkManager('invalid')

    def test_invalid_ppp_create(self):
        with pytest.raises(Exception, message = 'Invalid mode type: invalid-ppp'):
            networkManager = NetworkManager.NetworkManager('invalid-ppp')
