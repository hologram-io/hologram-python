# NovaM_R404.py - Hologram Python SDK Hologram Nova R404 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Modem import Modem
from Hologram.Event import Event
from UtilClasses import ModemResult

DEFAULT_R404_TIMEOUT = 200

class NovaM_R404(Modem):

    usb_ids = [('05c6', '90b2')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(NovaM_R404, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                         chatscript_file=chatscript_file, event=event)
        self._at_sockets_available = True

    def init_serial_commands(self):
        self.command("E0") #echo off
        self.command("+CMEE", "2") #set verbose error codes
        self.command("+CPIN?")
        #self.set_timezone_configs()
        #self.command("+CPIN", "") #set SIM PIN
        self.command("+CPMS", "\"ME\",\"ME\",\"ME\"")
        self.set_sms_configs()
        self.set_network_registration_status()

    def set_network_registration_status(self):
        self.command("+CEREG", "2")

    def is_registered(self):
        return self.check_registered('+CEREG')

    def disable_at_sockets_mode(self):
        self._at_sockets_available = False

    def close_socket(self, socket_identifier=None):

        if socket_identifier is None:
            socket_identifier = self.socket_identifier

        ok, r = self.set('+USOCL', "%s" % socket_identifier, timeout=40)
        if ok != ModemResult.OK:
            self.logger.error('Failed to close socket')

    @property
    def description(self):
        return 'Hologram Nova US 4G LTE Cat-M1 Cellular USB Modem (R404)'
