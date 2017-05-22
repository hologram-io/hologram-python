import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode.MockSerial import MockSerial

class TestSerial(object):

    first_buffer = 'AT\nAT\nAT\nAT\nAT\nAT+UPSD=0,7,"0.0.0.0"\r\r\nERROR\r\n'
    second_buffer = 'AT\nAT\nAT\nAT+UDOPN=12\r\r\n+UDOPN: 12,"T-Mobile"\r\n\r\nOK\r\n'

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

    def test_Serial_operator(self):
        serial = MockSerial()
        assert serial.operator == '34567890123456789'

    def test_get_at_response_from_buffer_csq(self):

        serial = MockSerial()
        serial.setSerialBuffer('AT+CSQ\r\r\n+CSQ: 13,4\r\n\r\nOK\r\n')
        response = serial._get_at_response_from_buffer('+CSQ')
        assert response.encode() == 'CSQ\r\r\n+CSQ: 13,4\r\n\r\nOK\r\n'

    def test_get_at_response_from_buffer_imsi(self):
        serial = MockSerial()
        serial.setSerialBuffer('AT\nAT+CIMI\r\r\n12345\r\n\r\nOK\r\n')
        response = serial._get_at_response_from_buffer('+CIMI')
        assert response.encode() == 'CIMI\r\r\n12345\r\n\r\nOK\r\n'

    def test_get_at_response_from_buffer_location(self):
        serial = MockSerial()
        serial.setSerialBuffer('AT\nAT\nAT\nAT\nAT\nAT\nAT\nAT+ULOC=2,2,0,360,10\r\r\nOK\r\n\r\n+UULOC: 16/05/2017,15:05:36.000,41.8893885,-87.6243304,201,235\r\n')
        response = serial._get_at_response_from_buffer('+UULOC')
        assert response.encode() == 'ULOC=2,2,0,360,10\r\r\nOK\r\n\r\n+UULOC: 16/05/2017,15:05:36.000,41.8893885,-87.6243304,201,235\r\n'

    def test_flush_used_response_from_serial_port_buffer(self):
        serial = MockSerial()

        serial.setSerialBuffer(self.first_buffer)
        serial._flush_used_response_from_serial_port_buffer('+UPSD')
        assert 'AT+UPSD=0,7,"0.0.0.0"\r\r\n' not in serial.getSerialBuffer()

        serial.setSerialBuffer(self.first_buffer + self.second_buffer)
        serial._flush_used_response_from_serial_port_buffer('+UDOPN')
        assert 'AT+UPSD=0,7,"0.0.0.0"\r\r\n' in serial.getSerialBuffer()

    def test_disable_sms(self):
        serial = MockSerial()
        assert serial.sms_disabled == True
