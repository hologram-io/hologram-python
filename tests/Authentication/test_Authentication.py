# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Authentication.py - This file implements unit tests for the Authentication
#                          class.

import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *

credentials = {'devicekey':'12345678'}

class TestAuthentication:

    def test_create(self):
        auth = Authentication.Authentication(credentials)
