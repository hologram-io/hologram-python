# CSRPSKAuthentication.py - Hologram Python SDK CSRPSK interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# This CSRPSKAuthentication file implements the CSRPSK authentication interface.
#
# LICENSE: Distributed under the terms of the MIT License
#
from Authentication import Authentication
import json

LEN_CLOUD_ID = 4
LEN_CLOUD_KEY = 4

class CSRPSKAuthentication(Authentication):

    def __init__(self, credentials):

        self.enforceValidCloudIDAndKey(credentials)
        super(CSRPSKAuthentication, self).__init__(credentials = credentials)

    def buildPayloadString(self, messages, topics=None):

        self.enforceValidCloudIDAndKey(self.credentials)

        self.buildAuthString()

        # Attach topic(s)
        if topics is not None:
            self.buildTopicString(topics)

        # Attach message(s)
        self.buildMessageString(messages)

        send_data = json.dumps(self.data)
        send_data += "\r\r"
        return send_data

    def buildSMSPayloadString(self, destination_number, message):

        self.enforceValidCloudIDAndKey(self.credentials)

        send_data = 'S' + self.credentials['cloud_id'] + self.credentials['cloud_key']
        send_data += destination_number + ' ' + message
        send_data += "\r\r"

        return send_data

    def buildAuthString(self, timestamp = None, sequence_number = None):
        self.storeCloudID()
        self.storeCloudKey()

    def buildTopicString(self, topics):
        self.storeTopics(topics)

    def buildMessageString(self, messages):
        self.storeMessages(messages)

    def enforceValidCloudIDAndKey(self, credentials):
        if not (credentials['cloud_id'] and credentials['cloud_key']):
            raise ValueError('Must set cloud_id and cloud_key to use CSRPSKAuthentication')
        elif (len(credentials['cloud_id']) != LEN_CLOUD_ID \
              or len(credentials['cloud_key']) != LEN_CLOUD_KEY):
            raise ValueError('Cloud id and key must each be 4 characters long')

    # EFFECTS: Stores the cloudID and cloudKey.
    def storeCloudID(self):
        self.data['s'] = self.credentials['cloud_id']

    def storeCloudKey(self):
        self.data['c'] = self.credentials['cloud_key']

    # EFFECTS: Stores the topic(s)
    def storeTopics(self, topics):
        self.data['t'] = topics

    # EFFECTS: Stores the cloud message(s).
    def storeMessages(self, messages):
        self.data['d'] = messages
