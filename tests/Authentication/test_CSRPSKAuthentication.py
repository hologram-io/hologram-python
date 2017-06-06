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
        assert "{\"k\": \"12345678\", \"d\": \"test without topics\"}\r\r" == auth.buildPayloadString(message)

    def test_invalid_device_key_length(self):
        credentials = {'devicekey': '12345678'}
        auth = CSRPSKAuthentication(credentials)
        auth.credentials['devicekey'] = '12345'
        with pytest.raises(SystemExit, message = 'AuthenticationError: Device key must be 8 characters long'):
            auth.buildPayloadString('test invalid device key')
