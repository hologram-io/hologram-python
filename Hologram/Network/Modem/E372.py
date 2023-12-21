# E372.py - Based on Hologram Python SDK Huawei MS2131 modem interface
#
#
#
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Hologram.Network.Modem import Modem
from Hologram.Event import Event

DEFAULT_E372_TIMEOUT = 200

class E372(Modem):

    usb_ids = [('12d1', '14c6')]

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                     chatscript_file=chatscript_file, event=event)

    def connect(self, timeout = DEFAULT_E372_TIMEOUT):
        return super().connect(timeout)

    def set_network_registration_status(self):
        self.command("+CREG", "2")
        self.command("+CGREG", "2")

    def disable_at_sockets_mode(self):
        pass

    @property
    def iccid(self):
        return self._basic_command('^ICCID?').lstrip('^ICCID: ')[:-1]
