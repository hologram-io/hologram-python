import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode.MockSerial import MockSerial

class TestSerial(object):

    def test_Serial_create(self):
        serial = MockSerial()

        assert serial.device_name == '/dev/ttyACM1'
        assert serial.baud_rate == 9600

    def test_Serial_iccid(self):
        serial = MockSerial()
        assert serial.iccid == '1234567890123456789'

    def test_Serial_imsi(self):
        serial = MockSerial()
        assert serial.imsi == '1234567890123456789'

    def test_Serial_signal_strength(self):
        serial = MockSerial()
        assert serial.signal_strength == '1234567890123456789'
