import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *
from Hologram.Credentials import Credentials

CSRPSKID = '1234'
CSRPSKKey = '5678'

credentials = Credentials(CSRPSKID, CSRPSKKey)

class TestCSRPSKAuthentication:

    def test_create(self):
        auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)

    def test_build_payload_string_without_topics(self):
        auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)
        message = "one two three"
        assert "{\"s\": \"1234\", \"c\": \"5678\", \"d\": \"one two three\"}\r\r" == auth.buildPayloadString(message)
