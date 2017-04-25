# HOTPAuthentication.py - Hologram Python SDK HOTPAuthentication interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import hashlib
import hmac
import struct
from HologramAuthentication import HologramAuthentication

DEVICE_ID_TYPE = 'C'
TOPIC_TYPE = 'T'
BINARY_TYPE = 'B'

DEFAULT_MODULUS = 1000000
class HOTPAuthentication(HologramAuthentication):

    def __init__(self, credentials, last_sequence_number=-1,
                 to_validate_sequence_number=True, modulus=DEFAULT_MODULUS):
        self._last_sequence_number = last_sequence_number
        self._to_validate_sequence_number = to_validate_sequence_number
        self._modulus = modulus
        self._payload = ''
        super(HOTPAuthentication, self).__init__(credentials)

    def buildPayloadString(self, messages, topics=None):
        super(HOTPAuthentication, self).buildPayloadString(messages,topics=topics)
        return self._payload

    def buildAuthString(self, timestamp=None, sequence_number=None):

        if timestamp == None:
            raise ValueError('HOTP Assertion Failure: Timestamp must be specified')

        self.__enforce_sequence_number(sequence_number)

        self.__update_sequence_number(sequence_number)

        self.__generate_auth_payload(timestamp, sequence_number)

    def __update_sequence_number(self, sequence_number):
        if sequence_number == None:
            self._last_sequence_number = self._last_sequence_number + 1
        else:
            self._last_sequence_number = sequence_number

    def __generate_auth_payload(self, timestamp, sequence_number):
        hmac_digest = hmac.new(self.credentials['private_key'],
                               struct.pack(">Q", sequence_number), hashlib.sha1).digest()

        i = ord(hmac_digest[19]) & 15
        self._payload = DEVICE_ID_TYPE + self.credentials['device_id'] + ' ' \
                        + str(timestamp) + ' ' \
                        + str((struct.unpack(">I", hmac_digest[i:i+4])[0] & 0x7fffffff) % self._modulus) + ' '

    def buildTopicString(self, topics):
        if type(topics) is str:
            topics = [topics]

        for topic in topics:
            self._payload += TOPIC_TYPE + str(topic) + chr(0)

    def buildMessageString(self, messages):
        if type(messages) is str:
            messages = [messages]

        for message in messages:
            self._payload += BINARY_TYPE + str(message) + chr(0)
        self._payload += chr(0)

    def __enforce_sequence_number(self, sequence_number):
        if self._to_validate_sequence_number == False or sequence_number == None:
            return

        if sequence_number <= self._last_sequence_number:
            raise ValueError('HOTP Assertion Failure: Sequence number must always \
                             be greater than last sequence number for \
                             cryptographically secure transport')
