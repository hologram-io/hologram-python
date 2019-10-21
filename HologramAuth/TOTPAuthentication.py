# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.7.4 (default, Sep  7 2019, 18:27:02) 
# [Clang 10.0.1 (clang-1001.0.46.4)]
# Embedded file name: build/bdist.linux-armv7l/egg/HologramAuth/TOTPAuthentication.py
# Compiled at: 2019-08-27 17:24:30
import hashlib, hmac, struct
from .HOTPAuthentication import HOTPAuthentication
DEFAULT_TIME_WINDOW = 30
DEVICE_ID_TYPE = 'C'

class TOTPAuthentication(HOTPAuthentication):

    def __init__(self, credentials, time_window=DEFAULT_TIME_WINDOW):
        self.time_window = time_window
        super(TOTPAuthentication, self).__init__(credentials=credentials)

    def buildAuthString(self, timestamp=None, sequence_number=None):
        timestamp = self.generate_timestamp(timestamp)
        sequence_number = timestamp // self.time_window
        self.__update_sequence_number(sequence_number)
        self.generate_auth_payload(timestamp, sequence_number)

    def __update_sequence_number(self, sequence_number):
        if sequence_number is None:
            self._last_sequence_number = self._last_sequence_number + 1
        else:
            self._last_sequence_number = sequence_number
        return

    def generate_auth_payload(self, timestamp, sequence_number):
        hmac_digest = hmac.new(self.credentials['private_key'], struct.pack('>Q', sequence_number), hashlib.sha1).digest()
        i = ord(hmac_digest[19]) & 15
        self._payload = DEVICE_ID_TYPE + self.credentials['device_id'] + ' ' + str(timestamp) + ' ' + str((struct.unpack('>I', hmac_digest[i:i + 4])[0] & 2147483647) % self._modulus) + ' '

    @property
    def time_window(self):
        return self._time_window

    @time_window.setter
    def time_window(self, time_window):
        self._time_window = time_window