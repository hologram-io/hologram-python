# Nova.py - Hologram Python SDK Nova modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Hologram.Network.Modem import Modem
from Hologram.Event import Event

DEFAULT_NOVA_TIMEOUT = 200

class Nova(Modem):

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
                                   chatscript_file=chatscript_file, event=event)

    def disable_at_sockets_mode(self):
        self._at_sockets_available = False

    def enable_at_sockets_mode(self):
        self._at_sockets_available = True

    def handleURC(self, urc):
        """
        Handles UBlox URC related AT command responses.

        :param urc: the URC string
        :type urc: string
        """
        self.logger.debug("URC! %s", urc)

        if urc.startswith('+CSIM: '):
            self.parse_and_populate_last_sim_otp_response(urc.lstrip('+CSIM: '))
            return
        elif urc.startswith('+UULOC: '):
            self._handle_location_urc(urc)
        elif urc.startswith('+UUSORD: '):

            # Strip UUSORD socket identifier + payload length from the URC event.
            # Example: {+UUSORD: 0,2} -> 0 and 2
            response_list = urc.lstrip('+UUSORD: ').split(',')
            socket_identifier = int(response_list[0])
            payload_length = int(response_list[-1])

            if self.urc_state == Modem.SOCKET_RECEIVE_READ:
                self._read_and_append_message_receive_buffer(socket_identifier, payload_length)
            else:
                self.socket_identifier = socket_identifier
                self.last_read_payload_length = payload_length
                self.urc_state = Modem.SOCKET_SEND_READ
        elif urc.startswith('+UUSOLI: '):
            self._handle_listen_urc(urc)
            self.last_read_payload_length = 0
            self.urc_state = Modem.SOCKET_RECEIVE_READ
        elif urc.startswith('+UUPSDD: '):
            self.event.broadcast('cellular.forced_disconnect')
        elif urc.startswith('+UUSOCL: '):
            self.urc_state = Modem.SOCKET_CLOSED

        super().handleURC(urc)

    def parse_and_populate_last_sim_otp_response(self, response):
        raise NotImplementedError('Must instantiate the right modem type')

    @property
    def version(self):
        return self._basic_command('I9')

