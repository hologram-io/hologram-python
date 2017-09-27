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
from UtilClasses import ModemResult

DEFAULT_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
DEFAULT_SERIAL_BAUD_RATE = 9600

class Serial(ISerial):

    def __init__(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                 baud_rate=DEFAULT_SERIAL_BAUD_RATE,
                 timeout=ISerial.DEFAULT_SERIAL_TIMEOUT,
                 event=Event()):
        super(Serial, self).__init__(device_name=device_name,
                                     baud_rate=DEFAULT_SERIAL_BAUD_RATE,
                                     timeout=timeout,
                                     event=event)


    def __del__(self):
        try:
            self.closeSerialPort()
        except Exception:
            pass


    def openSerialPort(self):

        try:
            self.serial_port = serial.Serial(self.device_name, baudrate=self.baud_rate,
                                             bytesize=8, parity='N', stopbits=1,
                                             timeout=self.timeout, write_timeout=1)
        except Exception as e:
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

    def __enforce_serial_port_open(self):
        if (not self.serial_port) or (not self.serial_port.isOpen()):
            raise Exception('Serial port not open')

    def write(self, message):
        self.serial_port.write(message.encode())
        self.serial_port.flush()

    def _read(self, timeout=None, size=ISerial.DEFAULT_SERIAL_READ_SIZE):
        if timeout is not None:
            self.serial_port.timeout = timeout
        r = self.serial_port.read(size)
        if timeout is not None:
            self.serial_port.timeout = timeout
        return r

    def command(self, cmd='', value=None, expected=None, timeout=None,
                retries=ISerial.DEFAULT_SERIAL_RETRIES, seteq=False, read=False,
                prompt=None, data=None, hide=False):
        try:
            return super(Serial, self).command(cmd, value, expected, timeout,
                    retries, seteq, read, prompt, data, hide)
        except serial.serialutil.SerialTimeoutException as e:
            self.logger.debug('unable to write to port')
            self.result = ModemResult.Error
        return self._commandResult()


    def readline(self, timeout=None, hide=False):
        # Override set timeout with the given timeout if necessary
        if timeout is not None:
            self.serial_port.timeout = timeout
        r = self.serial_port.readline()
        if len(r) > 0 and not hide:
            self.logger.debug('{' + r.rstrip('\r\n') + '}')
        # Revert back to original default timeout
        if timeout is not None:
            self.serial_port.timeout = self.timeout
        return r

    @property
    def serial_port(self):
        return self._serial_port

    @serial_port.setter
    def serial_port(self, serial_port):
        self._serial_port = serial_port
