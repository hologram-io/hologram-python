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
