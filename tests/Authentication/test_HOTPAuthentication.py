# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_HOTPAuthentication.py - This file implements unit tests for the
#                                HOTPAuthentication class.

import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from HologramAuth.HOTPAuthentication import HOTPAuthentication

credentials = {'devicekey': '12345678'}

class TestHOTPAuthentication(object):

    def test_create(self):
        auth = HOTPAuthentication(credentials)

