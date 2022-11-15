# Quectel.py - Hologram Python SDK Quectel modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import time
import binascii

from serial.serialutil import Timeout

from Hologram.Network.Modem import Modem
from Hologram.Event import Event
from UtilClasses import ModemResult
from Exceptions.HologramError import SerialError, NetworkError

class Quectel(Modem):

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                            chatscript_file=chatscript_file, event=event)
        self._at_sockets_available = True
        self.urc_response = ''

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

        return self.urc_response.rstrip('\r\n')

    def create_socket(self):
        self._set_up_pdp_context()

    def connect_socket(self, host, port):
        self.command('+QIOPEN', '1,0,\"TCP\",\"%s\",%d,0,1' % (host, port))
        # According to the Quectel Docs
        # Have to wait for URC response “+QIOPEN: <connectID>,<err>”

    def close_socket(self, socket_identifier=None):
        ok, _ = self.command('+QICLOSE', self.socket_identifier)
        if ok != ModemResult.OK:
            self.logger.error('Failed to close socket')
        self.urc_state = Modem.SOCKET_CLOSED
        self._tear_down_pdp_context()

    def write_socket(self, data):
        hexdata = binascii.hexlify(data)
        # We have to do it in chunks of 510 since 512 is actually too long (CMEE error)
        # and we need 2n chars for hexified data
        for chunk in self._chunks(hexdata, 510):
            value = '%d,\"%s\"' % (self.socket_identifier, chunk.decode())
            ok, _ = self.set('+QISENDEX', value, timeout=10)
            if ok != ModemResult.OK:
                self.logger.error('Failed to write to socket')
                raise NetworkError('Failed to write to socket')

    def read_socket(self, socket_identifier=None, payload_length=None):

        if socket_identifier is None:
            socket_identifier = self.socket_identifier

        if payload_length is None:
            payload_length = self.last_read_payload_length

        ok, resp = self.set('+QIRD', '%d,%d' % (socket_identifier, payload_length))
        if ok == ModemResult.OK:
            resp = resp.lstrip('+QIRD: ')
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

    def listen_socket(self, port):
        # No equivilent exists for quectel modems
        pass

    def is_registered(self):
        return self.check_registered('+CREG') or self.check_registered('+CEREG')

        # EFFECTS: Handles URC related AT command responses.
    def handleURC(self, urc):
        if urc.startswith('+QIOPEN: '):
            response_list = urc.lstrip('+QIOPEN: ').split(',')
            socket_identifier = int(response_list[0])
            err = int(response_list[-1])
            if err == 0:
                self.urc_state = Modem.SOCKET_WRITE_STATE
                self.socket_identifier = socket_identifier
            else:
                self.logger.error('Failed to open socket')
                raise NetworkError('Failed to open socket')
            return
        if urc.startswith('+QIURC: '):
            response_list = urc.lstrip('+QIURC: ').split(',')
            urctype = response_list[0]
            if urctype == '\"recv\"':
                self.urc_state = Modem.SOCKET_SEND_READ
                self.socket_identifier = int(response_list[1])
                self.last_read_payload_length = int(response_list[2])
                self.urc_response = self._readline_from_serial_port(5)
            if urctype == '\"closed\"':
                self.urc_state = Modem.SOCKET_CLOSED
                self.socket_identifier = int(response_list[-1])
            return
        super().handleURC(urc)

    def _is_pdp_context_active(self):
        if not self.is_registered():
            return False

        ok, r = self.command('+QIACT?')
        if ok == ModemResult.OK:
            try:
                pdpstatus = int(r.lstrip('+QIACT: ').split(',')[1])
                # 1: PDP active
                return pdpstatus == 1
            except (IndexError, ValueError) as e:
                self.logger.error(repr(e))
            except AttributeError as e:
                self.logger.error(repr(e))
        return False

    def set_network_registration_status(self):
        self.command("+CREG", "2")
        self.command("+CEREG", "2")

    def _set_up_pdp_context(self):
        if self._is_pdp_context_active(): return True
        self.logger.info('Setting up PDP context')
        self.set('+QICSGP', f'1,1,\"{self._apn}\",\"\",\"\",1')
        ok, _ = self.set('+QIACT', '1', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')