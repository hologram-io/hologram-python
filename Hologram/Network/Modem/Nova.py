# Nova.py - Hologram Python SDK Nova modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Modem import Modem
from Exceptions.HologramError import SerialError
from Hologram.Event import Event
from UtilClasses import ModemResult

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
        self._at_sockets_available = True


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

    def create_socket(self):
        self._set_up_pdp_context()
        super(Nova, self).create_socket()

    def is_registered(self):
        return self.check_registered('+CREG') or self.check_registered('+CGREG')

    # EFFECTS: Enforces that the Nova modem be in the correct mode to support multiple
    #          serial ports
    def enforce_nova_modem_mode(self):

        modem_mode = self.modem_mode
        self.logger.debug('USB modem mode: ' + str(modem_mode))

        # Set the modem mode to 0 if necessary.
        if modem_mode == 2:
            self.modem_mode = 0
            devices = self.detect_usable_serial_port()
            self.device_name = devices[0]
            super(Nova, self).initialize_serial_interface()

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

    # EFFECTS: Returns the sim otp response from the sim
    def get_sim_otp_response(self, command):

        self.command("+CSIM=46,\"008800801110" + command + "00\"", hide=True)

        while self.last_sim_otp_command_response is None:
            self.checkURC(hide=True)

        return self.last_sim_otp_command_response

    # EFFECTS: Handles URC related AT command responses.
    def handleURC(self, urc):
        if urc.startswith('+CSIM: '):
            self.parse_and_populate_last_sim_otp_response(urc.lstrip('+CSIM: '))
            return

        super(Nova, self).handleURC(urc)

    def disable_at_sockets_mode(self):
        self._at_sockets_available = False

    @property
    def location(self):
        temp_loc = self.last_location
        if self._set_up_pdp_context():
            self.last_location = None
            ok, r = self.set('+ULOC', '2,2,0,10,10')
            if ok != ModemResult.OK:
                self.logger.error('Location request failed')
                return None
            while self.last_location is None and self._is_pdp_context_active():
                self.checkURC()
        if self.last_location is None:
            self.last_location = temp_loc
        return self.last_location

    @property
    def description(self):
        return 'Hologram Nova Global 3G/2G Cellular USB Modem (U201)'
