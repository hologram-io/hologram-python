import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem import Modem

class TestModem(object):

    def test_modem_create(self):
        modem = Modem('ppp')
        assert repr(modem.mode) == 'PPP'

    def test_modem_serial_create(self):
        modem = Modem(mode = 'serial')
        assert repr(modem.mode) == 'Serial'

    def test_invalid_is_connected(self):
        modem = Modem('ppp')
        with pytest.raises(Exception, message = 'Must instantiate a Modem type'):
            modem.isConnected()

    def test_invalid_connect(self):
        modem = Modem('ppp')
        with pytest.raises(Exception, message = 'Must instantiate a Modem type'):
            modem.connect()

    def test_invalid_disconnect(self):
        modem = Modem('ppp')
        with pytest.raises(Exception, message = 'Must instantiate a Modem type'):
            modem.diconnect()