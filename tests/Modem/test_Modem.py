import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.MockModem import MockModem

class TestModem(object):

    def test_invalid_is_connected(self):
        modem = MockModem()
        with pytest.raises(Exception, message = 'Must instantiate a Modem type'):
            modem.isConnected()

    def test_invalid_connect(self):
        modem = MockModem()
        with pytest.raises(Exception, message = 'Must instantiate a Modem type'):
            modem.connect()

    def test_invalid_disconnect(self):
        modem = MockModem()
        with pytest.raises(Exception, message = 'Must instantiate a Modem type'):
            modem.diconnect()

    def test_get_result_string(self):
        modem = MockModem()
        assert modem.getResultString(0) == 'Modem returned OK'
        assert modem.getResultString(-1) == 'Modem timeout'
        assert modem.getResultString(-2) == 'Modem error'
        assert modem.getResultString(-3) == 'Modem response doesn\'t match expected return value'
        assert modem.getResultString(-99) == 'Unknown response code'
