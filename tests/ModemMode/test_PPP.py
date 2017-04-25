import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode.MockPPP import MockPPP

class TestPPP(object):

    def test_ppp_create(self):
        ppp = MockPPP(chatscript_file='test')

        assert ppp.device_name == '/dev/ttyUSB0'
        assert ppp.baud_rate == '9600'
        assert ppp.localIPAddress == None
        assert ppp.remoteIPAddress == None
        assert ppp.connect_script == '/usr/sbin/chat -v -f test'

    def test_ppp_invalid_chatscript_create(self):
        with pytest.raises(Exception, message='Must specify chatscript file'):
            ppp = MockPPP()
