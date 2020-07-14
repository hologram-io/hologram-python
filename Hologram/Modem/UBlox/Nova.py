# Nova.py - Hologram Python SDK Nova modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Hologram.Modem import Modem
from Hologram.Utils import ModemResult
from Hologram.Exceptions.HologramError import NetworkError
from Hologram.Event import Event

DEFAULT_NOVA_TIMEOUT = 200

class Nova(Modem):

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                   chatscript_file=chatscript_file, event=event)

    def disable_at_sockets_mode(self):
        self._at_sockets_available = False

    def enable_at_sockets_mode(self):
        self._at_sockets_available = True

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
        self.set('+UPSD', '0,1,\"hologram\"')
        self.set('+UPSD', '0,7,\"0.0.0.0\"')
        ok, _ = self.set('+UPSDA', '0,3', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')

    def enable_hex_mode(self):
        self.__set_hex_mode(1)

    def disable_hex_mode(self):
        self.__set_hex_mode(0)

    def __set_hex_mode(self, enable_hex_mode):
        self.command('+UDCONF', '1,%d' % enable_hex_mode)

    @property
    def modem_mode(self):
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

    @property
    def version(self):
        return self._basic_command('I9')

    @property
    def operator(self):
        op = self._basic_set('+UDOPN','12')
        if op is not None:
            return op.strip('"')
        return op
