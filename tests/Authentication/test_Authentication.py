import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *
from Hologram.Credentials import Credentials

CSRPSKID = '1234'
CSRPSKKey = '5678'

credentials = Credentials(CSRPSKID, CSRPSKKey)

class TestAuthentication:

    def test_create(self):
        auth = Authentication.Authentication(credentials)
