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

class CSRPSKAuthentication(Authentication):

    def __init__(self, credentials):
        super(CSRPSKAuthentication, self).__init__(credentials = credentials)

    def buildPayloadString(self, messages, topics=None):

        self.buildAuthString()

        # Attach topic(s)
        if topics is not None:
            self.buildTopicString(topics)

        # Attach message(s)
        self.buildMessageString(messages)

        send_data = json.dumps(self.data)
        send_data += "\r\r"
        print send_data
        return send_data

    def buildSMSPayloadString(self, destination_number, message):

        send_data = 'S' + self.credentials.cloud_id + self.credentials.cloud_key
        send_data += destination_number + ' ' + message
        send_data += "\r\r"

        print send_data
        return send_data

    def buildAuthString(self, timestamp = None, sequence_number = None):
        self.storeCloudID()
        self.storeCloudKey()

    def buildTopicString(self, topics):
        self.storeTopics(topics)

    def buildMessageString(self, messages):
        self.storeMessages(messages)
