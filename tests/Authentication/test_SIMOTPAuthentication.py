# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_SIMOTPAuthentication.py - This file implements unit tests for the
#                                SIMOTPAuthentication class.

import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from HologramAuth.SIMOTPAuthentication import SIMOTPAuthentication

credentials = {'devicekey': '12345678'}

class TestSIMOTPAuthentication(object):

    def test_create(self):
        auth = SIMOTPAuthentication(credentials)
        assert auth.time_window == 30

    def test_build_nonce_request_payload_string(self):
        auth = SIMOTPAuthentication(credentials)
        assert auth.buildNonceRequestPayloadString() == 'N'
