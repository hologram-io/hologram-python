# NovaM.py - Hologram Python SDK Hologram Nova R404/R410 modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016-2018 - Hologram, Inc
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Hologram.Network.Modem.Nova import Nova
from Hologram.Event import Event
from Exceptions.HologramError import NetworkError
from UtilClasses import ModemResult

DEFAULT_NOVAM_TIMEOUT = 200

class NovaM(Nova):

    usb_ids = [('05c6', '90b2')]
    module = 'option'
    syspath = '/sys/bus/usb-serial/drivers/option1/new_id'

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):
        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                         chatscript_file=chatscript_file, event=event)
        self._at_sockets_available = True
        modem_id = self.modem_id
        self.baud_rate = '115200'
        if("R404" in modem_id):
            self.is_r410 = False
        else:
            self.is_r410 = True

    def set_network_registration_status(self):
        self.command("+CEREG", "2")

    def is_registered(self):
        return self.check_registered('+CEREG')

    @property
    def description(self):
        modemtype = '(R410)' if self.is_r410 else '(R404)'
        return 'Hologram Nova US 4G LTE Cat-M1 Cellular USB Modem ' + modemtype

    @property
    def location(self):
        raise NotImplementedError('The R404 and R410 do not support Cell Locate at this time')

    # same as Modem::connect_socket except with longer timeout
    def connect_socket(self, host, port):
        at_command_val = "%d,\"%s\",%s" % (self.socket_identifier, host, port)
        ok, _ = self.set('+USOCO', at_command_val, timeout=122)
        if ok != ModemResult.OK:
            self.logger.error('Failed to connect socket')
            raise NetworkError('Failed to connect socket')
        else:
            self.logger.info('Connect socket is successful')

    def reset(self):
        self.set('+CFUN', '15') # restart the modem
