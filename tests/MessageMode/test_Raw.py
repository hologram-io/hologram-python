import pytest
import sys
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *
from Hologram.Credentials import Credentials
from Hologram.Raw import Raw

CSRPSKID = '1234'
CSRPSKKey = '5678'

credentials = Credentials(CSRPSKID, CSRPSKKey)

auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)

class TestRaw(object):

    def test_create(self):
        raw = Raw(auth)
        assert raw.send_host == ''
        assert raw.send_port == ''

        raw.send_host = 'test.com'
        raw.send_port = '9999'

        assert raw.send_host == 'test.com'
        assert raw.send_port == '9999'

    def test_invalid_send_sms(self):
        raw = Raw(auth)

        temp = "hello"
        with pytest.raises(NotImplementedError, message = 'Cannot send SMS via custom Cloud'):
            raw.sendSMS('+1234567890', temp)
