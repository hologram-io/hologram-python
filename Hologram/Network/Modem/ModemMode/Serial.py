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
import time
from ISerial import ISerial
from ....Event import Event

DEFAULT_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
DEFAULT_SERIAL_BAUD_RATE = 9600

class Serial(ISerial):

    def __init__(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                 baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=1,
                 event=Event()):
        super(Serial, self).__init__(device_name=device_name,
                                     baud_rate=DEFAULT_SERIAL_BAUD_RATE,
                                     timeout=timeout,
                                     event=event)

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

    def write(self, msg, expected_response=None):

        self._serial_port_lock.writer_acquire()

        if expected_response is None:
            expected_response = msg

        self.__enforce_serial_port_open()

        command = 'AT' + msg + "\r"
        self.logger.info('write command: ' + command)

        self.serial_port.write(command.encode())
        self.serial_port.flush()

        self._serial_port_buffer += self.serial_port.read(256)
        self._serial_port_lock.writer_release()

        self._serial_port_lock.reader_acquire()

        while self._serial_port_buffer.find(expected_response) == -1:
            self._serial_port_lock.reader_release()

            self._poll_and_read_from_serial_port(timeout=1)

            self._serial_port_lock.reader_acquire()

        self._serial_port_lock.reader_release()

        # Remove used AT command from the serial port buffer.
        response = self._get_at_response_from_buffer(expected_response)
        self._flush_used_response_from_serial_port_buffer(expected_response)
        return self._filter_return_values_from_at_response(msg, response)

    def __enforce_serial_port_open(self):
        if (not self.serial_port) or (not self.serial_port.isOpen()):
            raise Exception('Serial port not open')
