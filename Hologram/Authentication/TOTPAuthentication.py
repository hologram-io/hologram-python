# TOTPAuthentication.py - Hologram Python SDK TOTPAuthentication interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from HOTPAuthentication import HOTPAuthentication

DEFAULT_TIME_WINDOW = 30

class TOTPAuthentication(HOTPAuthentication):

    def __init__(self, credentials, time_window=DEFAULT_TIME_WINDOW):
        # time module is only used if a timestamp is not provided when
        # generating auth string
        self.time_window = time_window
        super(TOTPAuthentication, self).__init__(credentials=credentials)

    def buildAuthString(self, timestamp=None, sequence_number=None):
        self.time = None
        if (timestamp == None):
            # no timestamp argument was provided
            if (self.time == None):
                # time module has not yet been imported, so import
                self.time = __import__('time')
            # generate current timestamp
            timestamp = int(self.time.mktime(self.time.localtime()))

        timestamp = int(timestamp)

        return super(TOTPAuthentication, self).buildAuthString(timestamp=timestamp,
                                                               sequence_number=timestamp//self.time_window)

    @property
    def time_window(self):
        return self._time_window

    @time_window.setter
    def time_window(self, time_window):
        self._time_window = time_window
