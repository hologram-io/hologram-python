# Authentication.py - Hologram Python SDK Authentication interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import logging

class Authentication(object):

    def __init__(self, credentials):
        self.credentials = credentials

        # Logging setup.
        self.logger = logging.getLogger(type(self).__name__)

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, credentials):
        self._credentials = credentials
