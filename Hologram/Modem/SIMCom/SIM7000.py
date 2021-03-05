# SIM7000.py - Hologram Python SDK SIMCom SIM7000 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import binascii
import time

from serial.serialutil import Timeout

from Hologram.Modem import Modem
from Hologram.Event import Event
from Hologram.Utils import ModemResult
from Hologram.Exceptions import SerialError, NetworkError

DEFAULT_SIM7000_TIMEOUT = 200

class SIM7000(Modem):
    usb_ids = [('1e0e', '9001')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                        chatscript_file=chatscript_file, event=event)
        self._at_sockets_available = True
        self.urc_response = ''

    def connect(self, timeout=DEFAULT_SIM7000_TIMEOUT):

        success = super().connect(timeout)

        # put serial mode on other port
        if success is True:
            # detect another open serial port to use for PPP
            devices = self.detect_usable_serial_port()
            if not devices:
                raise SerialError('Not enough serial ports detected for Nova')
            self.logger.debug('Moving connection to port %s', devices[0])
            self.device_name = devices[0]
            super().initialize_serial_interface()

        return success

    def send_message(self, data, timeout=Modem.DEFAULT_SEND_TIMEOUT):
        # Waiting for the open socket urc
        while self.urc_state != Modem.SOCKET_WRITE_STATE:
            self.checkURC()

        self.write_socket(data)

        loop_timeout = Timeout(timeout)
        while self.urc_state != Modem.SOCKET_SEND_READ:
            self.checkURC()
            if self.urc_state != Modem.SOCKET_SEND_READ:
                if loop_timeout.expired():
                    raise SerialError('Timeout occurred waiting for message status')
                time.sleep(self._RETRY_DELAY)
            elif self.urc_state == Modem.SOCKET_CLOSED:
                return '[1,0]' #this is connection closed for hologram cloud response

        return self.urc_response

    def create_socket(self):
        self._set_up_pdp_context()

    def connect_socket(self, host, port):
        self.command('+CIPSTART', '\"TCP\",\"%s\",%d' % (host, port))
        self.urc_state = Modem.SOCKET_WRITE_STATE

    def close_socket(self, socket_identifier=None):
        ok, _ = self.command('+CIPCLOSE')
        if ok != ModemResult.OK:
            self.logger.error('Failed to close socket')
        self.urc_state = Modem.SOCKET_CLOSED

    def write_socket(self, data):
        hexdata = binascii.hexlify(data)
        # We have to do it in chunks of 510 since 512 is actually too long (CMEE error)
        # and we need 2n chars for hexified data
        for chunk in self._chunks(hexdata, 510):
            value = '%d,\"%s\"' % (self.socket_identifier, chunk.decode())
            ok, _ = self.command('+CIPSEND', len(value), timeout=10, expected="SEND OK", prompt=">", data=value)
            if ok != ModemResult.OK:
                self.logger.error('Failed to write to socket')
                raise NetworkError('Failed to write to socket')

    def read_socket(self, socket_identifier=None, payload_length=None):
        if payload_length is None:
            payload_length = self.last_read_payload_length

        ok, resp = self.set('+CIPRXGET', '1,%d' % (payload_length))
        if ok == ModemResult.OK:
            if resp is not None:
                resp = resp.strip('"')
            try:
                resp = resp.decode()
            except:
                # This is some sort of binary data that can't be decoded so just
                # return the bytes. We might want to make this happen via parameter
                # in the future so it is more deterministic
                self.logger.debug('Could not decode recieved data')

            return resp

    def is_registered(self):
        return self.check_registered('+CREG') or self.check_registered('+CGREG')

    # EFFECTS: Handles URC related AT command responses.
    def handleURC(self, urc):
        # Figure out what urcs there are to handle
        super().handleURC(urc)

    def _is_pdp_context_active(self):
        if not self.is_registered():
            return False

        ok, r = self.command('+CIPSTATUS', expected="STATE: IP START")
        return ok == ModemResult.OK:

    def init_serial_commands(self):
        self.command("E0") #echo off
        self.command("+CMEE", "2") #set verbose error codes
        self.command("+CPIN?")
        self.set_timezone_configs()
        #self.command("+CPIN", "") #set SIM PIN
        self.command("+CPMS", "\"ME\",\"ME\",\"ME\"")
        self.command("+CNMP", "38")
        self.command("+CMNB", "1")
        self.set_sms_configs()
        self.set_network_registration_status()

    def set_network_registration_status(self):
        self.command("+CREG", "2")
        self.command("+CGREG", "2")

    def _set_up_pdp_context(self):
        if self._is_pdp_context_active(): return True
        ok, _ = self.command('+CIPSTATUS', expected="STATE: IP INITIAL")
        while ok != ModemResult.OK:
            self.command('+CIPSHUT')
            ok, _ = self.command('+CIPSTATUS', expected="STATE: IP INITIAL")

        self.set('+CSTT', '\"hologram\"')
        self.set('+CIICR', timeout=30)
        if not self._is_pdp_context_active():
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')

    @property
    def description(self):
        return 'SIMCom SIM7000'