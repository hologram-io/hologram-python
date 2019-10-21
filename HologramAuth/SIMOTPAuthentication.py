# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.7.4 (default, Sep  7 2019, 18:27:02) 
# [Clang 10.0.1 (clang-1001.0.46.4)]
# Embedded file name: build/bdist.linux-armv7l/egg/HologramAuth/SIMOTPAuthentication.py
# Compiled at: 2019-08-27 17:24:30
from .Holohash import Holohash
from .HOTPAuthentication import HOTPAuthentication
DEVICE_ID_TYPE = 'H'
NONCE_REQUEST_TYPE = 'N'
DEFAULT_TIME_WINDOW = 30

class SIMOTPAuthentication(HOTPAuthentication):

    def __init__(self, credentials, time_window=DEFAULT_TIME_WINDOW):
        self.time_window = time_window
        self.holohash_client = Holohash()
        self.iccid = None
        self.sim_otp_token = None
        super(SIMOTPAuthentication, self).__init__(credentials=credentials)
        return

    def buildAuthString(self, timestamp=None, sequence_number=None):
        self._payload = DEVICE_ID_TYPE + self.iccid + ' ' + self.timestamp + ' ' + self.sim_otp_token + ' '

    def buildNonceRequestPayloadString(self):
        return str(NONCE_REQUEST_TYPE)

    def generate_sim_otp_command(self, imsi=None, iccid=None, nonce=None, timestamp=None):
        self.timestamp = str(self.generate_timestamp(timestamp))
        self.iccid = iccid
        return self.holohash_client.generate_sim_gsm_milenage_command(imsi, iccid, nonce, self.timestamp)

    def generate_sim_otp_token(self, response):
        self.sim_otp_token = self.holohash_client.generate_milenage_token(response, self.timestamp)

    @property
    def time_window(self):
        return self._time_window

    @time_window.setter
    def time_window(self, time_window):
        self._time_window = time_window