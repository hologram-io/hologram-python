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
from HologramAuthentication import HologramAuthentication

DEVICE_KEY_LEN = 8

class CSRPSKAuthentication(HologramAuthentication):

    def __init__(self, credentials):
        self._data = {}
        super(CSRPSKAuthentication, self).__init__(credentials=credentials)

    def buildPayloadString(self, messages, topics=None, modem_type=None,
                           modem_id=None, version=None):

        self.enforceValidDeviceKey()

        super(CSRPSKAuthentication, self).buildPayloadString(messages,
                                                             topics=topics,
                                                             modem_type=modem_type,
                                                             modem_id=modem_id,
                                                             version=version)

        return json.dumps(self._data) + "\r\r"

    def buildSMSPayloadString(self, destination_number, message):

        self.enforceValidDeviceKey()

        send_data = 'S' + self.credentials['devicekey']
        send_data += destination_number + ' ' + message
        send_data += "\r\r"

        return send_data

    def buildAuthString(self, timestamp=None, sequence_number=None):
        self._data['k'] = self.credentials['devicekey']

    def buildMetadataString(self, modem_type, modem_id, version):

        self._data['m'] = self.metadata_version \
                          + self.build_modem_type_id_str(modem_type, modem_id) \
                          + '-' + str(version)

    def buildTopicString(self, topics):
        self._data['t'] = topics

    def buildMessageString(self, messages):
        self._data['d'] = messages

    def enforceValidDeviceKey(self):
        if type(self.credentials) is not dict:
            raise AuthenticationError('Credentials is not a dictionary')
        elif not (self.credentials['devicekey']):
            raise AuthenticationError('Must set devicekey to use CSRPSKAuthentication')
        elif len(self.credentials['devicekey']) != DEVICE_KEY_LEN:
            raise AuthenticationError('Device key must be %d characters long' % DEVICE_KEY_LEN)
