import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode import PPP

class TestPPP(object):

    def test_ppp_create(self):
        ppp = PPP(chatScriptFile = 'test')

        assert ppp.deviceName == '/dev/ttyUSB0'
        assert ppp.baudRate == '9600'
        assert ppp.isConnected() == 0
        assert ppp.localIPAddress == None
        assert ppp.remoteIPAddress == None

    def test_ppp_invalid_chatscript_create(self):
        with pytest.raises(Exception, message = 'Must specify chatscript file'):
            ppp = PPP()
