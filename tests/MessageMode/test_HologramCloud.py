import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *
from Hologram.Credentials import Credentials
from Hologram.HologramCloud import HologramCloud

CSRPSKID = '1234'
CSRPSKKey = '5678'

credentials = Credentials(CSRPSKID, CSRPSKKey)

auth = CSRPSKAuthentication.CSRPSKAuthentication(credentials)

class TestHologramCloud(object):

    def test_invalid_sms_length(self):
        cloud = HologramCloud(auth)

        temp = '111111111234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
        with pytest.raises(Exception, message = 'SMS cannot be more than 160 characters long!'):
            cloud.sendSMS('+1234567890', temp)
