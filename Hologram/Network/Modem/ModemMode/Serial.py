# Serial.py - Hologram Python SDK Modem Serial interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import serial
from ISerial import ISerial

DEFAULT_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
DEFAULT_SERIAL_BAUD_RATE = 9600

class Serial(ISerial):

    def __init__(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                 baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=1):
        super(Serial, self).__init__(device_name=device_name,
                                     baud_rate=DEFAULT_SERIAL_BAUD_RATE,
                                     timeout=timeout)

    def openSerialPort(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                       baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=1):

        try:
            self.serial_port = serial.Serial(device_name, baudrate=baud_rate,
                                             bytesize=8, parity='N', stopbits=1,
                                             timeout=timeout)
        except Exception:
            self.logger.error('Failed to initialize serial port')
            return False

        if not self.serial_port.isOpen():
            self.logger.error('Failed to open serial port')
            return False

        return True

    def closeSerialPort(self):

        self.__enforce_serial_port_open()

        try:
            self.serial_port.close()
        except Exception:
            self.logger.error('Failed to close serial port')

    def write(self, msg):

        self.__enforce_serial_port_open()

        command = 'AT' + msg + "\r"
        self.logger.info('write command: ' + command)

        self.serial_port.write(command.encode())
        self.serial_port.flush()

        response = self.serial_port.read(256)
        return self._filter_response(msg, response)

    def __enforce_serial_port_open(self):
        if (not self.serial_port) or (not self.serial_port.isOpen()):
            raise Exception('Serial port not open')

