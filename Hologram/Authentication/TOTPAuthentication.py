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

class TOTPAuthentication(HOTPAuthentication):

    def __init__(self, credentials, time_window = 30):
        # time module is only used if a timestamp is not provided when
        # generating auth string
        self.time = None
        self.time_window = time_window
        super(TOTPAuthentication, self).__init__(credentials = credentials)

    # EFFECTS: Builds the payload string that is going to be sent
    def buildPayloadString(self, messages, topics = None):
        return super(TOTPAuthentication, self).buildPayloadString(
                                                            messages = messages,
                                                            topics = topics)

    def buildAuthString(self, timestamp = None, sequence_number = None):
        if (timestamp == None):
            # no timestamp argument was provided
            if (self.time == None):
                # time module has not yet been imported, so import
                self.time = __import__("time")
            # generate current timestamp
            timestamp = int(self.time.mktime(self.time.localtime()))
        elif (not (timestamp is int)):
            timestamp = int(timestamp)

        return super(TOTPAuthentication, self).buildAuthString(
                                timestamp = timestamp,
                                sequence_number = timestamp//self.time_window)

    def buildTopicString(self, topics):
        return super(TOTPAuthentication, self).buildTopicString(topics = topics)

    def buildMessageString(self, messages):
        return super(TOTPAuthentication, self).buildMessageString(
                                                        messages = messages)

    def setTimeWindow(self, timeWindow):
        self.time_window = timeWindow
