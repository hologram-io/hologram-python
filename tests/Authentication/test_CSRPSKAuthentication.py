# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_CSRPSKAuthentication.py - This file implements unit tests for the
#                                CSRPSKAuthentication class.

import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication.CSRPSKAuthentication import CSRPSKAuthentication

class TestCSRPSKAuthentication(object):

    def test_create(self):
        credentials = {'devicekey': '12345678'}
        auth = CSRPSKAuthentication(credentials)

    def test_build_payload_string_without_topics(self):
        credentials = {'devicekey': '12345678'}
        auth = CSRPSKAuthentication(credentials)
        message = 'test without topics'
        assert "{\"k\": \"12345678\", \"m\": \"\\u0001e303-None\", \"d\": \"test without topics\"}\r\r" \
            == auth.buildPayloadString(message, modem_type='E303')

    def test_build_payload_string_with_empty_modem_type_and_id(self):
        credentials = {'devicekey': '12345678'}
        auth = CSRPSKAuthentication(credentials)
        message = 'test with empty modem_type and modem_id'
        assert "{\"k\": \"12345678\", \"m\": \"\\u0001agnostic-None\", \"d\": \"test with empty modem_type and modem_id\"}\r\r" \
            == auth.buildPayloadString(message, modem_type=None)

    def test_invalid_device_key_length(self):
        credentials = {'devicekey': '12345678'}
        auth = CSRPSKAuthentication(credentials)
        auth.credentials['devicekey'] = '12345'
        with pytest.raises(Exception, message = 'AuthenticationError: Device key must be 8 characters long'):
            auth.buildPayloadString('test invalid device key')
