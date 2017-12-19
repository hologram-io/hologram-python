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
from Hologram.Event import Event

DEFAULT_NOVA_TIMEOUT = 200

class Nova(Modem):

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(Nova, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                   chatscript_file=chatscript_file, event=event)

    def disable_at_sockets_mode(self):
        self._at_sockets_available = False
