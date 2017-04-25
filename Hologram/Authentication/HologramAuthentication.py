# Authentication.py - Hologram Python SDK Authentication interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from Authentication import Authentication

class HologramAuthentication(Authentication):

    def __init__(self, credentials):
        super(HologramAuthentication, self).__init__(credentials)

    def buildPayloadString(self, messages, topics=None):
        self.buildAuthString()

        # Attach topic(s)
        if topics is not None:
            self.buildTopicString(topics)

        # Attach message(s)
        self.buildMessageString(messages)

    def buildAuthString(self, timestamp=None, sequence_number=None):
        raise NotImplementedError('Must instantiate a subclass of HologramAuthentication')

    def buildTopicString(self, topics):
        raise NotImplementedError('Must instantiate a subclass of HologramAuthentication')

    def buildMessageString(self, messages):
        raise NotImplementedError('Must instantiate a subclass of HologramAuthentication')
