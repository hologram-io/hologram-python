# CSRPSKAuthentication.py - Hologram Python SDK CSRPSKAuthentication interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# This CSRPSKAuthentication file implements the CSRPSK authentication interface.
#
# LICENSE: Distributed under the terms of the MIT License
#
import json
from Exceptions.HologramError import AuthenticationError
from Hologram.Authentication.HologramAuthentication import HologramAuthentication

DEVICE_KEY_LEN = 8

class CSRPSKAuthentication(HologramAuthentication):

    def __init__(self, credentials):
        self._data = {}
        super().__init__(credentials=credentials)

    def buildPayloadString(self, messages, topics=None, modem_type=None,
                           modem_id=None, version=None):

        self.enforceValidDeviceKey()

        super().buildPayloadString(messages,
                                   topics=topics,
                                   modem_type=modem_type,
                                   modem_id=modem_id,
                                   version=version)

        payload = json.dumps(self._data) + "\r\r"
        return payload.encode()

    def buildSMSPayloadString(self, destination_number, message):

        self.enforceValidDeviceKey()

        send_data = 'S' + self.credentials['devicekey']
        send_data += destination_number + ' ' + message
        send_data += "\r\r"

        return send_data.encode()

    def buildAuthString(self, timestamp=None, sequence_number=None):
        self._data['k'] = self.credentials['devicekey']

    def buildMetadataString(self, modem_type, modem_id, version):

        formatted_string = f"{self.build_modem_type_id_str(modem_type, modem_id)}-{version}"
        self._data['m'] = self.metadata_version.decode() + formatted_string

    def buildTopicString(self, topics):
        self._data['t'] = topics

    def buildMessageString(self, messages):
        self._data['d'] = messages

    def enforceValidDeviceKey(self):
        if not isinstance(self.credentials, dict):
            raise AuthenticationError('Credentials is not a dictionary')
        elif not self.credentials['devicekey']:
            raise AuthenticationError('Must set devicekey to use CSRPSKAuthentication')
        elif len(self.credentials['devicekey']) != DEVICE_KEY_LEN:
            raise AuthenticationError('Device key must be %d characters long' % DEVICE_KEY_LEN)
