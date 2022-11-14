# BG96.py - Hologram Python SDK Quectel BG96 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Hologram.Network.Modem import Quectel
from Hologram.Event import Event
from UtilClasses import ModemResult

DEFAULT_BG96_TIMEOUT = 200

class BG96(Quectel):
    usb_ids = [('2c7c', '0296')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                        chatscript_file=chatscript_file, event=event)
        
    def connect(self, timeout=DEFAULT_BG96_TIMEOUT):
        success = super().connect(timeout)

    def _tear_down_pdp_context(self):
        if not self._is_pdp_context_active(): return True
        self.logger.info('Tearing down PDP context')
        ok, _ = self.set('+QIACT', '0', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context tear down failed')
        else:
            self.logger.info('PDP context deactivated')

    @property
    def description(self):
        return 'Quectel BG96'
