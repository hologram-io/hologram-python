import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode import Serial

class TestSerial(object):

    def test_Serial_create(self):
        serial = Serial()

        assert serial.deviceName == '/dev/ttyUSB0'
        assert serial.baudRate == '9600'
        assert serial.isConnected() == 0
        assert serial.localIPAddress == None
        assert serial.remoteIPAddress == None
