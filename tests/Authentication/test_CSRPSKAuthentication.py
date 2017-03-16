import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *

class TestCSRPSKAuthentication(object):

    def test_create(self):
        credentials = {'cloud_id': '1234', 'cloud_key': '5678'}
        auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)

    def test_build_payload_string_without_topics(self):
        credentials = {'cloud_id': '1234', 'cloud_key': '5678'}
        auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)
        message = "one two three"
        assert "{\"s\": \"1234\", \"c\": \"5678\", \"d\": \"one two three\"}\r\r" == auth.buildPayloadString(message)

    def test_invalid_cloud_id_length(self):
        credentials = {'cloud_id': '1234', 'cloud_key': '5678'}
        auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)
        auth.credentials['cloud_id'] = '12345'
        with pytest.raises(Exception, message = 'Cloud id and key must each be 4 characters long'):
            auth.buildPayloadString("hi there")

    def test_invalid_cloud_key_length(self):
        credentials = {'cloud_id': '1234', 'cloud_key': '5678'}
        auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)
        auth.credentials['cloud_key'] = '12345'
        with pytest.raises(Exception, message = 'Cloud id and key must each be 4 characters long'):
            auth.buildSMSPayloadString('+12345678900', 'hi there')

    def test_unset_cloud_id_length(self):
        credentials = {'cloud_key': '5678'}
        with pytest.raises(Exception, message = 'Must set cloud_id and cloud_key to use CSRPSKAuthentication'):
            auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)
