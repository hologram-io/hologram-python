# HOTPAuthentication.py - Hologram Python SDK HOTPAuthentication interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import hmac
import struct
import hashlib
from Authentication import Authentication

class HOTPAuthentication(Authentication):

    def __init__(self, credentials, last_sequence_number = -1, validate_sequence_number = True, modulus = 1000000):
        self.last_sequence_number = last_sequence_number
        self.validate_sequence_number = validate_sequence_number
        self.modulus = modulus
        super(HOTPAuthentication, self).__init__(credentials)

    def buildPayloadString(self, messages, topics=None):
        # Simple PSK auth
        output = self.buildAuthString() + " "

        # Attach to topic(s)
        if topics is not None:
            output += self.buildTopicString(topics)

        # Attach message(s)
        output += self.buildMessageString(messages)
        output += chr(0)
        return output

    def buildAuthString(self, timestamp = None, sequence_number = None):

        if (timestamp == None):
            raise ValueError("HOTP Assertion Failure: Timestamp must be specified")
        if (sequence_number == None):
            sequence_number = self.last_sequence_number + 1
        if ((not self.validate_sequence_number) or (sequence_number > self.last_sequence_number)):
            self.last_sequence_number = sequence_number
            # HOTP algorithm
            hmac_digest = hmac.new(self.credentials.private_key, struct.pack(">Q", sequence_number), hashlib.sha1).digest()
            i = ord(hmac_digest[19]) & 15
            return "C" + self.credentials.device_id + " " + str(timestamp) + " " + str((struct.unpack(">I", hmac_digest[i:i+4])[0] & 0x7fffffff) % self.modulus)
        else:
            raise ValueError("HOTP Assertion Failure: Sequence number must always be greater than last sequence number for cryptographically secure transport")

    def buildTopicString(self, topics):

        self.storeTopics(topics)

        output = ""
        if type(topics) is str:
            topics = [topics]
        for topic in topics:
            output += "T" + str(topic) + chr(0)
        return output

    def buildMessageString(self, messages):

        self.storeMessages(messages)

        output = ""
        if type(messages) is str:
            messages = [messages]
        for message in messages:
            output += "B" + str(message) + chr(0)
        return output

    def setValidateSequenceNumber(self, toValidate):
        self.validate_sequence_number = toValidate
