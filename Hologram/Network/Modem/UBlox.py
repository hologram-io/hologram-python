# UBlox.py - Hologram Python SDK Ublox modem interface
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

from Hologram.Network.Modem import Modem
from Hologram.Event import Event
from Exceptions.HologramError import NetworkError
from UtilClasses import ModemResult

class Ublox(Modem):

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                   chatscript_file=chatscript_file, event=event)

    def disable_at_sockets_mode(self):
        self._at_sockets_available = False

    def enable_at_sockets_mode(self):
        self._at_sockets_available = True

    def create_socket(self):
        op = self._basic_set('+USOCR', '6', strip_val=False)
        if op is not None:
            self.socket_identifier = int(op)

    # REQUIRES: The host and port.
    # EFFECTS: Issues an AT command to connect to the specified socket identifier.
    def connect_socket(self, host, port):
        at_command_val = "%d,\"%s\",%s" % (self.socket_identifier, host, port)
        ok, _ = self.set('+USOCO', at_command_val, timeout=20)
        if ok != ModemResult.OK:
            self.logger.error('Failed to connect socket')
            raise NetworkError('Failed to connect socket')
        else:
            self.logger.info('Connect socket is successful')

    def listen_socket(self, port):
        at_command_val = "%d,%s" % (self.socket_identifier, port)
        self.listen_socket_identifier = self.socket_identifier
        ok, _ = self.set('+USOLI', at_command_val, timeout=5)
        if ok != ModemResult.OK:
            self.logger.error('Failed to listen socket')
            raise NetworkError('Failed to listen socket')

    def write_socket(self, data):
        self.enable_hex_mode()
        hexdata = binascii.hexlify(data)
        # We have to do it in chunks of 510 since 512 is actually too long (CMEE error)
        # and we need 2n chars for hexified data
        for chunk in self._chunks(hexdata, 510):
            value = b'%d,%d,\"%s\"' % (self.socket_identifier,
                    len(binascii.unhexlify(chunk)),
                    chunk)
            ok, _ = self.set('+USOWR', value, timeout=10)
            if ok != ModemResult.OK:
                self.logger.error('Failed to write to socket')
                raise NetworkError('Failed to write socket')
        self.disable_hex_mode()

    def read_socket(self, socket_identifier=None, payload_length=None):
        if socket_identifier is None:
            socket_identifier = self.socket_identifier

        if payload_length is None:
            payload_length = self.last_read_payload_length

        self.enable_hex_mode()

        resp = self._basic_set('+USORD', '%d,%d' % (socket_identifier, payload_length))
        if resp is not None:
            resp = resp.strip('"')
        bytedata = binascii.unhexlify(resp)
        try:
            resp = bytedata.decode()
        except:
            # This is some sort of binary data that can't be decoded so just
            # return the bytes. We might want to make this happen via parameter
            # in the future so it is more deterministic
            resp = bytedata

        self.disable_hex_mode()
        return resp

    def close_socket(self, socket_identifier=None):

        if socket_identifier is None:
            socket_identifier = self.socket_identifier

        ok, r = self.set('+USOCL', "%s" % socket_identifier)
        if ok != ModemResult.OK:
            self.logger.info('Failed to close socket')

    def handleURC(self, urc):
        """
        Handles UBlox URC related AT command responses.

        :param urc: the URC string
        :type urc: string
        """
        self.logger.debug("URC! %s", urc)

        if urc.startswith('+CSIM: '):
            self.parse_and_populate_last_sim_otp_response(urc.lstrip('+CSIM: '))
            return
        elif urc.startswith('+UULOC: '):
            self._handle_location_urc(urc)
        elif urc.startswith('+UUSORD: '):

            # Strip UUSORD socket identifier + payload length from the URC event.
            # Example: {+UUSORD: 0,2} -> 0 and 2
            response_list = urc.lstrip('+UUSORD: ').split(',')
            socket_identifier = int(response_list[0])
            payload_length = int(response_list[-1])

            if self.urc_state == Modem.SOCKET_RECEIVE_READ:
                self._read_and_append_message_receive_buffer(socket_identifier, payload_length)
            else:
                self.socket_identifier = socket_identifier
                self.last_read_payload_length = payload_length
                self.urc_state = Modem.SOCKET_SEND_READ
        elif urc.startswith('+UUSOLI: '):
            self._handle_listen_urc(urc)
            self.last_read_payload_length = 0
            self.urc_state = Modem.SOCKET_RECEIVE_READ
        elif urc.startswith('+UUPSDD: '):
            self.event.broadcast('cellular.forced_disconnect')
        elif urc.startswith('+UUSOCL: '):
            self.urc_state = Modem.SOCKET_CLOSED

        super().handleURC(urc)

    def _is_pdp_context_active(self):
        if not self.is_registered():
            return False

        ok, r = self.set('+UPSND', '0,8')
        if ok == ModemResult.OK:
            try:
                pdpstatus = int(r.lstrip('UPSND: ').split(',')[2])
                # 1: PDP active
                return pdpstatus == 1
            except (IndexError, ValueError) as e:
                self.logger.error(repr(e))
        return False

    def _set_up_pdp_context(self):
        if self._is_pdp_context_active(): return True
        self.logger.info('Setting up PDP context')
        self.set('+UPSD', f'0,1,\"{self._apn}\"')
        self.set('+UPSD', '0,7,\"0.0.0.0\"')
        ok, _ = self.set('+UPSDA', '0,3', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')

    def _tear_down_pdp_context(self):
        if not self._is_pdp_context_active(): return True
        self.logger.info('Tearing down PDP context')
        ok, _ = self.set('+UPSDA', '0,4', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context tear down failed')
        else:
            self.logger.info('PDP context deactivated')

    def enable_hex_mode(self):
        self.command('+UDCONF', '1,1')

    def disable_hex_mode(self):
        self.command('+UDCONF', '1,0')

    @property
    def modem_usb_mode(self):
        mode_number = None
        # trim:
        # +UUSBCONF: 0,"",,"0x1102" -> 0
        # +UUSBCONF: 2,"ECM",,"0x1104" -> 2
        try:
            ok, res = self.read('+UUSBCONF')
            if ok == ModemResult.OK:
                mode_number = int(res.lstrip('+UUSBCONF: ').split(',')[0])
        except (IndexError, ValueError) as e:
            self.logger.error(repr(e))
        return mode_number

    @modem_usb_mode.setter
    def modem_usb_mode(self, mode):
        self.set('+UUSBCONF', str(mode))
        self.logger.info('Restarting modem')
        self.reset()
        self.logger.info('Modem restarted')
        self.closeSerialPort()
        time.sleep(Modem.DEFAULT_MODEM_RESTART_TIME)

