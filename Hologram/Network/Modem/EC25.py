# EC25.py - Hologram Python SDK Quectel EC25 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2025 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Hologram.Network.Modem.Quectel import Quectel
from UtilClasses import ModemResult

DEFAULT_EC21_TIMEOUT = 200


class EC25(Quectel):
    usb_ids = [("2c7c", "0125")]

    def connect(self, timeout=DEFAULT_EC21_TIMEOUT):
        success = super().connect(timeout)
        return success

    def _tear_down_pdp_context(self):
        if not self._is_pdp_context_active():
            return True
        self.logger.info("Tearing down PDP context")
        ok, _ = self.set("+QIDEACT", "1", timeout=30)
        if ok != ModemResult.OK:
            self.logger.error("PDP Context tear down failed")
        else:
            self.logger.info("PDP context deactivated")

    @property
    def description(self):
        return "Quectel EC25"
