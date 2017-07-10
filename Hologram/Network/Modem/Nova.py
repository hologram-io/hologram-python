# Nova.py - Hologram Python SDK Nova modem interface
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

NOVA_PPP_DEVICE_NAME = '/dev/ttyACM0'
NOVA_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
DEFAULT_NOVA_TIMEOUT = 200

class Nova(Modem):

    def __init__(self, device_name=NOVA_PPP_DEVICE_NAME, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(Nova, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                   chatscript_file=chatscript_file, event=event)
        # We need to enforce multi serial port support. We then reinstantiate
        # the serial interface with the correct device name.
        self.enforce_nova_modem_mode()
        self._serial_mode = Serial(device_name=NOVA_SERIAL_DEVICE_NAME, event=self.event)

    def isConnected(self):
        return self._mode.connected()

    def connect(self, timeout = DEFAULT_NOVA_TIMEOUT):
        return self._mode.connect(timeout = timeout)

    def disconnect(self):
        return self._mode.disconnect()

    # EFFECTS: Enforces that the Nova modem be in the correct mode to support multiple
    #          serial ports
    def enforce_nova_modem_mode(self):

        modem_mode = self._serial_mode.modem_mode
        self.logger.debug('USB modem mode: ' + str(modem_mode))

        # Set the modem mode to 0 if necessary.
        if modem_mode == 2:
            self._serial_mode.modem_mode = 0
