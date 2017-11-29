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


# pylint: disable=W0212
from Hologram.Network.Modem.Modem import Modem
class TestModemProtectedMethods(object):
    def test_check_registered_string(self):
        result = '+CREG: 2,5,"5585","404C790",6'
        registered = Modem._check_registered_helper('+CREG', result)
        assert registered == True

    def test_check_registered_short_list(self):
        result = ['+CREG: 5,"5585","404C78A",6',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 2,5,"5585","404C790",6']
        registered = Modem._check_registered_helper('+CREG', result)
        assert registered == True

    def test_check_registered_long_list(self):
        result = ['+CREG: 5,"5585","404EF4D",6',
                  '+CREG: 5,"5585","404C816",6',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 5,"5585","404C816",6',
                  '+CREG: 5,"5585","404EF4D",6',
                  '+CREG: 5,"5585","404C78A",6',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 5,"5585","404C816",6',
                  '+CREG: 2',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 2,5,"5585","404C790",6']
        registered = Modem._check_registered_helper('+CREG', result)
        assert registered == True
