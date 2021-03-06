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
from enum import Enum

from serial.serialutil import Timeout

from Hologram.Network.Modem import Modem
from Hologram.Event import Event
from UtilClasses import ModemResult
from Exceptions.HologramError import SerialError, NetworkError

DEFAULT_SIM7000_TIMEOUT = 200

class NetworkState(Enum):
    INITIAL = 'IP INITIAL'
    START = 'IP START'
    CONFIG = 'IP CONFIG'
    GPRSACT = 'IP GPRSACT'
    STATUS = 'IP STATUS'
    TCPCONN = 'TCP CONNECTING'
    UDPCONN = 'UDP CONNECTING'
    LISTENING = 'SERVER LISTENING'
    CONNECTED = 'CONNECT OK'
    TCPCLOSING = 'TCP CLOSING'
    UDPCLOSING = 'UDP CLOSING'
    TCPCLOSED = 'TCP CLOSED'
    UDPCLOSED = 'UDP CLOSED'
    DISCONNECTED = 'PDP DEACT'


class SIM7000(Modem):
    usb_ids = [('1e0e', '9001')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                        chatscript_file=chatscript_file, event=event)
        self._at_sockets_available = True
        self.urc_response = ''
        self.network_state = NetworkState.DISCONNECTED

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
        return self.check_registered('+CREG') or self.check_registered('+CEREG')

    def checkURC(self, hide=False):
        # Not all SIMCOM urcs have a + in front
        while(True):
            response = self._readline_from_serial_port(0, hide=hide)
            if len(response) > 0 and (response.startswith('+') or response.startswith('STATE') or response in ['CONNECT', 'CONNECT OK', 'CONNECT FAIL', 'SEND OK', 'ALREADY CONNECT', 'CLOSED']):
                urc = response.rstrip('\r\n')
                self.handleURC(urc)
            else:
                return

    def handleURC(self, urc):
        if urc.startswith('STATE'):
            urc = urc.lstrip('STATE: ')
            self.network_state = NetworkState(urc)
            return 
        elif urc == 'CONNECT OK':
            self.urc_state = Modem.SOCKET_WRITE_STATE
        elif urc == 'CLOSED':
            self.urc_state = Modem.SOCKET_CLOSED
        else:
            super().handleURC(urc)

    def _is_pdp_context_active(self):
        if not self.is_registered():
            return False

        self.command('+CIPSTATUS')
        self.checkURC()
        return self.network_state is NetworkState.CONNECTED

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
        time.sleep(0.5)

    def set_network_registration_status(self):
        self.command("+CREG", "2")
        self.command("+CEREG", "2")

    def _set_up_pdp_context(self):
        if self._is_pdp_context_active(): return True
        self.command('+CIPSTATUS')
        self.checkURC()
        while self.network_state is not NetworkState.INITIAL:
            self.command('+CIPSHUT')
            self.command('+CIPSTATUS')
            self.checkURC()

        self.set('+CSTT', '\"hologram\"')
        self.command('+CIICR', timeout=30)
        time.sleep(1)
        if not self._is_pdp_context_active():
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')

    @property
    def description(self):
        return 'SIMCom SIM7000'