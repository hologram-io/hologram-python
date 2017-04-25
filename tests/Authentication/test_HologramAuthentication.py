import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication.HologramAuthentication import HologramAuthentication

credentials = {'devicekey': '12345678'}

class TestHologramAuthentication(object):

    def test_create(self):
        auth = HologramAuthentication(credentials)

    def test_invalid_auth_string(self):
        auth = HologramAuthentication(credentials)
        with pytest.raises(Exception, message = 'Must instantiate a subclass of HologramAuthentication'):
            auth.buildPayloadString('test msg', 'test topic')

    def test_invalid_topic_string(self):
        auth = HologramAuthentication(credentials)
        with pytest.raises(Exception, message = 'Must instantiate a subclass of HologramAuthentication'):
            auth.buildTopicString('test topic')

    def test_invalid_msg_string(self):
        auth = HologramAuthentication(credentials)
        with pytest.raises(Exception, message = 'Must instantiate a subclass of HologramAuthentication'):
            auth.buildMessageString('test msg')
