# Authentication.py - Hologram Python SDK Authentication interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
class Authentication(object):

    def __init__(self, credentials):
        self.data = {}
        self.credentials = credentials

    def buildPayloadString(self, messages, topics=None):
        raise NotImplementedError("Must instantiate a subclass of the Authentication class")

    def validateAuthMessage(self):
        return True

    # EFFECTS: Stores the cloudID and cloudKey.
    def storeDeviceID(self):
        self.data['C'] = self.credentials.device_id

    def storePrivateKey(self):
        self.data['k'] = self.credentials.private_key

    def storeCloudID(self):
        self.data['s'] = self.credentials.cloud_id

    def storeCloudKey(self):
        self.data['c'] = self.credentials.cloud_key

    # EFFECTS: Stores the topic(s)
    def storeTopics(self, topics):
        self.data['t'] = topics

    # EFFECTS: Stores the cloud message(s).
    def storeMessages(self, messages):
        self.data['d'] = messages
