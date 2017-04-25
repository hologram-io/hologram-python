import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *

credentials = {'devicekey':'12345678'}

class TestAuthentication:

    def test_create(self):
        auth = Authentication.Authentication(credentials)
