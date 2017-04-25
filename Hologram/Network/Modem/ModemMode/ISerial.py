# ISerial.py - Hologram Python SDK Modem ISerial interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from ModemMode import ModemMode

DEFAULT_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
DEFAULT_SERIAL_BAUD_RATE = 9600

class ISerial(ModemMode):

    def __init__(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                 baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=1):

        super(ISerial, self).__init__(device_name=device_name, baud_rate=baud_rate)
        self.carrier = None
        self.serial_port = None

        self.openSerialPort(device_name=self.device_name, baud_rate=self.baud_rate,
                            timeout=timeout)

    def write(self, msg):
        raise NotImplementedError('Must instantiate a Serial type')

    def openSerialPort(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                       baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=1):
        raise NotImplementedError('Must instantiate a Serial type')

    def closeSerialPort(self):
        raise NotImplementedError('Must instantiate a Serial type')

    # EFFECTS: Cuts out the response from the echoed serial output.
    def _filter_response(self, msg, response):
        if msg not in response:
            raise Exception('Executed AT command not found in response')

        regEx = "\r\n" + msg + ': '
        return response.strip('AT' + msg).strip(regEx).strip("OK\r\n")

    @property
    def carrier(self):
        return self._carrier

    @carrier.setter
    def carrier(self, carrier):
        self._carrier = carrier

    # EFFECTS: Returns the Received Signal Strength Indication (RSSI) value of the modem
    @property
    def signal_strength(self):
        return self.write('+CSQ')

    @property
    def imsi(self):
        return self.write('+CIMI')

    @property
    def iccid(self):
        return self.write('+CCID')

    @property
    def cell_locate(self):
        return self.write('+ULOC')

    @property
    def serial_port(self):
        return self._serial_port

    @serial_port.setter
    def serial_port(self, serial_port):
        self._serial_port = serial_port
