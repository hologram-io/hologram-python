import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from HologramAuth.HOTPAuthentication import HOTPAuthentication

credentials = {'devicekey': '12345678'}

class TestHOTPAuthentication(object):

    def test_create(self):
        auth = HOTPAuthentication(credentials)

