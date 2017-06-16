import pytest
import sys
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *
from Hologram.Cloud import Cloud

class TestCloud(object):

    def test_create_send(self):
        cloud = Cloud(None, send_host = '127.0.0.1', send_port = 9999)

        assert cloud.send_host == '127.0.0.1'
        assert cloud.send_port == 9999
        assert cloud.receive_host == ''
        assert cloud.receive_port == 0

    def test_create_receive(self):
        cloud = Cloud(None, receive_host = '127.0.0.1', receive_port = 9999)

        assert cloud.send_host == ''
        assert cloud.send_port == 0
        assert cloud.receive_host == '127.0.0.1'
        assert cloud.receive_port == 9999

    def test_invalid_send_message(self):
        cloud = Cloud(None, receive_host = '127.0.0.1', receive_port = 9999)

        with pytest.raises(Exception, message = 'Must instantiate a Cloud type'):
            cloud.sendMessage("hello SMS")

    def test_invalid_send_sms(self):
        cloud = Cloud(None, send_host = '127.0.0.1', send_port = 9999)

        with pytest.raises(Exception, message = 'Must instantiate a Cloud type'):
            cloud.sendSMS('+12345678900', 'hello SMS')

    # This is good for testing if we updated the internal SDK version numbers before release.
    def test_sdk_version(self):
        cloud = Cloud(None, send_host = '127.0.0.1', send_port = 9999)

        assert cloud.version == '0.5.14'
