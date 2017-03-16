import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *

CSRPSKID = '1234'
CSRPSKKey = '5678'

credentials = {'cloud_id':CSRPSKID, 'cloud_key':CSRPSKKey}

class TestAuthentication:

    def test_create(self):
        auth = Authentication.Authentication(credentials)
