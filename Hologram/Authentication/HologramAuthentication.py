# HologramAuthentication.py - Hologram Python SDK HologramAuthentication interface
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

    def buildPayloadString(self, messages, topics=None, modem_type=None,
                           modem_id=None, version=None):

        self.buildAuthString()

        self.buildMetadataString(modem_type, modem_id, version)

        # Attach topic(s)
        if topics is not None:
            self.buildTopicString(topics)

        # Attach message(s)
        self.buildMessageString(messages)

    def buildAuthString(self, timestamp=None, sequence_number=None):
        raise NotImplementedError('Must instantiate a subclass of HologramAuthentication')

    def buildMetadataString(self, modem_type, modem_id, version):
        raise NotImplementedError('Must instantiate a subclass of HologramAuthentication')

    def buildTopicString(self, topics):
        raise NotImplementedError('Must instantiate a subclass of HologramAuthentication')

    def buildMessageString(self, messages):
        raise NotImplementedError('Must instantiate a subclass of HologramAuthentication')

    # EFFECTS: Builds the encoded modem type + id string.
    #          Used to build out metadata string.
    def build_modem_type_id_str(self, modem_type, modem_id):

        # Handle agnostic cases separately.
        if modem_type is None:
            return 'agnostic'

        payload = str(modem_type.lower())

        if modem_type == 'Nova':
            payload += ('-' + str(modem_id))
        return payload

    @property
    def metadata_version(self):
        return b'\x01'
