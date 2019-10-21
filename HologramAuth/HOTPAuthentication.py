# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.7.4 (default, Sep  7 2019, 18:27:02) 
# [Clang 10.0.1 (clang-1001.0.46.4)]
# Embedded file name: build/bdist.linux-armv7l/egg/HologramAuth/HOTPAuthentication.py
# Compiled at: 2019-08-27 17:24:30
from Hologram.Authentication.HologramAuthentication import HologramAuthentication
TOPIC_TYPE = 'T'
BINARY_TYPE = 'B'
METADATA_COMPACT_TYPE = 'M'
DEFAULT_MODULUS = 1000000

class HOTPAuthentication(HologramAuthentication):

    def __init__(self, credentials, last_sequence_number=-1, to_validate_sequence_number=True, modulus=DEFAULT_MODULUS):
        self._last_sequence_number = last_sequence_number
        self._to_validate_sequence_number = to_validate_sequence_number
        self._modulus = modulus
        self._payload = ''
        super(HOTPAuthentication, self).__init__(credentials)

    def buildPayloadString(self, messages, topics=None, modem_type=None, modem_id=None, version=None):
        super(HOTPAuthentication, self).buildPayloadString(messages, topics=topics, modem_type=modem_type, modem_id=modem_id, version=version)
        return self._payload

    def buildAuthString(self, timestamp=None, sequence_number=None):
        raise NotImplementedError('Internal Authentication error: Must define a HOTPAuthentication type')

    def buildMetadataString(self, modem_type, modem_id, version):
        self._payload += METADATA_COMPACT_TYPE + self.metadata_version + self.build_modem_type_id_str(modem_type, modem_id) + '-' + str(version) + chr(0)

    def buildTopicString(self, topics):
        if type(topics) is str:
            topics = [
             topics]
        for topic in topics:
            self._payload += TOPIC_TYPE + str(topic) + chr(0)

    def buildMessageString(self, messages):
        if type(messages) is str:
            messages = [
             messages]
        for message in messages:
            self._payload += BINARY_TYPE + str(message) + chr(0)

        self._payload += chr(0)

    def enforce_sequence_number(self, sequence_number):
        if self._to_validate_sequence_number == False or sequence_number == None:
            return
        assert not sequence_number <= self._last_sequence_number, 'HOTP Assertion Failure: Sequence number must always                              be greater than last sequence number for                              cryptographically secure transport'
        return

    def generate_timestamp(self, timestamp):
        self.time = None
        if timestamp == None:
            if self.time == None:
                self.time = __import__('time')
            timestamp = int(self.time.mktime(self.time.localtime()))
        timestamp = int(timestamp)
        assert not timestamp == None, 'HOTP Assertion Failure: Timestamp must be specified'
        return timestamp