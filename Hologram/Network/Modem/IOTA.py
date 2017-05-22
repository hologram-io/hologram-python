# IOTA.py - Hologram Python SDK IOTA modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from ModemMode import Serial
from Modem import Modem
from ...Event import Event

IOTA_PPP_DEVICE_NAME = '/dev/ttyACM0'
IOTA_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
DEFAULT_IOTA_TIMEOUT = 200

class IOTA(Modem):

    def __init__(self, device_name=IOTA_PPP_DEVICE_NAME, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(IOTA, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                   chatscript_file=chatscript_file, event=event)
        # We need to enforce multi serial port support. We then reinstantiate
        # the serial interface with the correct device name.
        self.enforce_iota_modem_mode()
        self._serial_mode = Serial(device_name=IOTA_SERIAL_DEVICE_NAME, event=self.event)

    def isConnected(self):
        return self._mode.connected()

    def connect(self, timeout = DEFAULT_IOTA_TIMEOUT):
        return self._mode.connect(timeout = timeout)

    def disconnect(self):
        return self._mode.disconnect()

    # EFFECTS: Enforces that the iota be in the correct mode to support multiple
    #          serial ports
    def enforce_iota_modem_mode(self):

        modem_mode = self._serial_mode.modem_mode
        self.logger.debug('USB modem mode: ' + str(modem_mode))

        # Set the modem mode to 0 if necessary.
        if modem_mode == 2:
            self._serial_mode.modem_mode = 0
