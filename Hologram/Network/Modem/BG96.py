# E303.py - Hologram Python SDK Huawei E303 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import binascii

from Hologram.Network.Modem import Modem
from Hologram.Event import Event
from UtilClasses import ModemResult
from Exceptions.HologramError import SerialError, NetworkError

DEFAULT_BG96_TIMEOUT = 200

class BG96(Modem):
    usb_ids = [('2c7c', '0296')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                        chatscript_file=chatscript_file, event=event)
        self._at_sockets_available = True

    def connect(self, timeout=DEFAULT_BG96_TIMEOUT):

        success = super().connect(timeout)

        # put serial mode on other port
        # if success is True:
        #     # detect another open serial port to use for PPP
        #     devices = self.detect_usable_serial_port()
        #     if not devices:
        #         raise SerialError('Not enough serial ports detected for Nova')
        #     self.logger.debug('Moving connection to port %s', devices[0])
        #     self.device_name = devices[0]
        #     super().initialize_serial_interface()

        return success

    def create_socket(self):
        self._set_up_pdp_context()

    def connect_socket(self, host, port):
        self.command('+QIOPEN', '1,0,\"TCP\",\"%s\",%d,0,1' % (host, port))

    def close_socket(self, socket_identifier=None):
        self.command('+QICLOSE', '1')

    def write_socket(self, data):
        hexdata = binascii.hexlify(data)
        # We have to do it in chunks of 510 since 512 is actually too long (CMEE error)
        # and we need 2n chars for hexified data
        for chunk in self._chunks(hexdata, 510):
            value = '1,\"%s\"' % chunk.decode()
            ok, _ = self.command('+QISENDEX', value, timeout=10)
            if ok != ModemResult.OK:
                self.logger.error('Failed to write to socket')
                raise NetworkError('Failed to write socket')

    def is_registered(self):
        return self.check_registered('+CREG') or self.check_registered('+CGREG')

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

    def _set_up_pdp_context(self):
        if self._is_pdp_context_active(): return True
        self.logger.info('Setting up PDP context')
        self.set('+QICSGP', '1,1,\"hologram\",\"\",\"\",1')
        ok, _ = self.set('+QIACT', '1', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')

    @property
    def description(self):
        return 'Quecetel BG96'