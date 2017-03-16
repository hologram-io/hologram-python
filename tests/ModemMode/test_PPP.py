import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode import PPP

class TestPPP(object):

    def test_ppp_create(self):
        ppp = PPP()

        assert ppp.deviceName == '/dev/ttyUSB0'
        assert ppp.baudRate == '9600'
        assert ppp.isConnected() == 0
        assert ppp.localIPAddress == None
        assert ppp.remoteIPAddress == None
