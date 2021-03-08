# BG96.py - Hologram Python SDK Quectel BG96 modem interface
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

from Hologram.Network.Modem import Modem
from Hologram.Event import Event
from UtilClasses import ModemResult
from Exceptions.HologramError import SerialError, NetworkError

DEFAULT_BG96_TIMEOUT = 200

class LE910(Modem):
    usb_ids = [('1bc7', '0036')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                        chatscript_file=chatscript_file, event=event)
        self._at_sockets_available = True
        self.urc_response = ''

    def connect(self, timeout=DEFAULT_BG96_TIMEOUT):

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
        self.write_socket(data)

        return self.read_socket(payload_length=5)

    def create_socket(self):
        self._set_up_pdp_context()
        # <connId>,<srMode>,<recvDataMode>,<keepalive>[,<ListenAutoRsp>[,<sendDataMode>]]
        ok, _ = self.command('#SCFGEXT', '1,2,0,1,0,1')
        if ok != ModemResult.OK:
            self.logger.error('Failed to configure socket')
            raise NetworkError('Failed to configure socket')

    def connect_socket(self, host, port):
        ok, _ = self.command('#SD', '1,0,%d,\"%s\",0,0,1' % (port, host))
        if ok != ModemResult.OK:
            self.logger.error('Failed to open socket')
            raise NetworkError('Failed to open socket')

        self.socket_identifier = 1
        self.urc_state = Modem.SOCKET_WRITE_STATE

    def close_socket(self, socket_identifier=None):
        ok, _ = self.command('#SH', self.socket_identifier)
        if ok != ModemResult.OK:
            self.logger.error('Failed to close socket')
        self.urc_state = Modem.SOCKET_CLOSED

    def write_socket(self, data):
        hexdata = binascii.hexlify(data)
        ok, _ = self.command('#SSENDEXT', "%d,%d" % (self.socket_identifier, len(hexdata)), prompt='>', data=hexdata.decode(), timeout=10)
        if ok != ModemResult.OK:
            self.logger.error('Failed to write to socket')
            raise NetworkError('Failed to write to socket')
        

    def read_socket(self, socket_identifier=None, payload_length=None):

        if socket_identifier is None:
            socket_identifier = self.socket_identifier

        if payload_length is None:
            payload_length = self.last_read_payload_length

        self.command('#SRECV', '%d,%d' % (socket_identifier, payload_length), read=False)
        loop_timeout = Timeout(Modem.DEFAULT_SEND_TIMEOUT)
        while self.urc_state != Modem.SOCKET_SEND_READ:
            self.checkURC()
            if self.urc_state != Modem.SOCKET_SEND_READ:
                if loop_timeout.expired():
                    raise SerialError('Timeout occurred waiting for message status')
                time.sleep(self._RETRY_DELAY)
            elif self.urc_state == Modem.SOCKET_CLOSED:
                return '[1,0]' #this is connection closed for hologram cloud response
        return self.urc_response

    def is_registered(self):
        return self.check_registered('+CREG') or self.check_registered('+CGREG') or self.check_registered('+CEREG')

    def checkURC(self, hide=False):
        while(True):
            response = self._readline_from_serial_port(0, hide=hide)
            if len(response) > 0 and (response.startswith('+') or response in ['SRING']):
                urc = response.rstrip('\r\n')
                self.handleURC(urc)
            else:
                return

    # EFFECTS: Handles URC related AT command responses.
    def handleURC(self, urc):
        if urc.startswith('SRING:'):
            # <srMode> = 2 (Data view):
            # SRING: <connId>,<recData>,<data>
            response_list = urc.lstrip('SRING:').split(',')
            self.urc_state = Modem.SOCKET_SEND_READ
            self.socket_identifier = int(response_list[0])
            self.last_read_payload_length = int(response_list[1])
            self.urc_response = response_list[2]
            return
        super().handleURC(urc)

    def _is_pdp_context_active(self):
        if not self.is_registered():
            return False

        ok, r = self.command('#SGACT?')
        if ok == ModemResult.OK:
            try:
                pdpstatus = int(r.lstrip('#SGACT: ').split(',')[1])
                # 1: PDP active
                return pdpstatus == 1
            except (IndexError, ValueError) as e:
                self.logger.error(repr(e))
            except AttributeError as e:
                self.logger.error(repr(e))
        return False

    def init_serial_commands(self):
        self.command("E0") #echo off
        self.command("+CMEE", "2") #set verbose error codes
        self.command("+CPIN?")
        self.set_timezone_configs()
        #self.command("+CPIN", "") #set SIM PIN
        self.command("+CPMS", "\"ME\",\"ME\",\"ME\"")
        self.set_sms_configs()
        self.set_network_registration_status()

    def set_network_registration_status(self):
        self.command("+CREG", "2")
        self.command("+CGREG", "2")
        self.command("+CEREG", "2")

    def _set_up_pdp_context(self):
        if self._is_pdp_context_active(): return True
        self.logger.info('Setting up PDP context')
        self.set('+CGDCONT', '1,\"IP\",\"hologram\"')
        ok, _ = self.set('#SGACT', '1,1', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')

    @property
    def description(self):
        return 'Telit LE910'