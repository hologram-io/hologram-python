import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode.MockSerial import MockSerial

class TestSerial(object):

    first_buffer = 'AT\nAT\nAT\nAT\nAT\nAT+UPSD=0,7,"0.0.0.0"\r\r\nERROR\r\n'
    second_buffer = 'AT\nAT\nAT\nAT+UDOPN=12\r\r\n+UDOPN: 12,"T-Mobile"\r\n\r\nOK\r\n'

    def test_serial_create(self):
        serial = MockSerial()

        assert serial.device_name == '/dev/ttyACM1'
        assert serial.baud_rate == 9600

    def test_serial_write(self):
        serial = MockSerial()
        msg = 'bla'
        response = 'AT' + msg + '\r\r\n' + msg + ': 1234567890123456789\r\n\r\nOK\r\n'
        assert serial.write(msg) == response

    def test_serial_readline(self):
        serial = MockSerial()

        serial.serial_port = 'bla'
        response = serial.readline(timeout=5)
        assert response == 'bla'
        assert serial.timeout == 1

        serial.serial_port = None
        response = serial.readline(timeout=5)
        assert response == None
        assert serial.timeout == 1

    def test_populate_location_obj(self):
        serial = MockSerial()
        location = serial.populate_location_obj('26/07/2017,12:12:12.000,41.8889,-87.62,0,601')
        assert location.date == '26/07/2017'
        assert location.time == '12:12:12.000'
        assert location.latitude == '41.8889'
        assert location.longitude == '-87.62'
        assert location.altitude == '0'
        assert location.uncertainty == '601'

    def test_debugwrite(self):
        serial = MockSerial()
        msg = 'add more'

        serial.debugwrite(msg)
        assert serial.debug_out == msg

        # serial buffer should now have more messages
        serial.debugwrite(msg)
        assert serial.debug_out == msg + msg

    def test_modemwrite(self):
        serial = MockSerial()

        cmd = 'cmd test'
        serial.modemwrite(cmd, start=True, at=True, seteq=True)
        assert serial.debug_out == '[AT' + cmd + '='

        serial.modemwrite(cmd, start=True)
        assert serial.debug_out == '[' + cmd

    def test_process_response(self):
        #serial.process_response('+CCID', timeout=None)
        pass

    def test_handleURC(self):
        pass
