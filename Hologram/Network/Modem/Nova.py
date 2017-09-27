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

DEFAULT_NOVA_TIMEOUT = 200

class Nova(Modem):
    usb_ids = [('1546','1102'),('1546','1104')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(Nova, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                   chatscript_file=chatscript_file, event=event)
        # We need to enforce multi serial port support. We then reinstantiate
        # the serial interface with the correct device name.
        self.enforce_nova_modem_mode()


    def connect(self, timeout = DEFAULT_NOVA_TIMEOUT):

        success = super(Nova, self).connect(timeout)

        # put serial mode on other port
        if success is True:
            # detect another open serial port to use for PPP
            devices = self.detect_usable_serial_port()
            if not devices:
                raise SerialError('Not enough serial ports detected for Nova')
            self.device_name = devices[0]
            super(Nova, self).initialize_serial_interface()

        return success

    # EFFECTS: Enforces that the Nova modem be in the correct mode to support multiple
    #          serial ports
    def enforce_nova_modem_mode(self):

        modem_mode = self._serial_mode.modem_mode
        self.logger.debug('USB modem mode: ' + str(modem_mode))

        # Set the modem mode to 0 if necessary.
        if modem_mode == 2:
            self._serial_mode.modem_mode = 0
            devices = self.detect_usable_serial_port()
            self.device_name = devices[0]
            super(Nova, self).initialize_serial_interface()