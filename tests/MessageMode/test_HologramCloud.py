import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *
from Hologram.HologramCloud import HologramCloud

CSRPSKID = '1234'
CSRPSKKey = '5678'

credentials = {'cloud_id':CSRPSKID, 'cloud_key':CSRPSKKey}

class TestHologramCloud(object):

    def test_create(self):
        hologram = HologramCloud(credentials, enable_inbound = False)

        assert hologram.send_host == 'cloudsocket.hologram.io'
        assert hologram.send_port == 9999
        assert hologram.receive_host == '0.0.0.0'
        assert hologram.receive_port == 4010

    def test_invalid_sms_length(self):

        hologram = HologramCloud(credentials, enable_inbound = False)

        temp = '111111111234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
        with pytest.raises(Exception, message = 'SMS cannot be more than 160 characters long!'):
            hologram.sendSMS('+1234567890', temp)