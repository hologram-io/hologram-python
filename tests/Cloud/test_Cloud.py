# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Cloud.py - This file implements unit tests for the Cloud class.

import pytest
import sys
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication import *
from Hologram.Cloud import Cloud
from Hologram.Network import Network

from tests.MockModem import MockModem

def mock_scan(network):
    return ['MockModem']

@pytest.fixture
def no_modem(monkeypatch):
    monkeypatch.setattr(Network, '_scan_for_modems', mock_scan)
    monkeypatch.setattr(Network, '_modemHandlers', {'MockModem': MockModem})

def test_create_send(no_modem):
    cloud = Cloud(None, send_host = '127.0.0.1', send_port = 9999)

    assert cloud.send_host == '127.0.0.1'
    assert cloud.send_port == 9999
    assert cloud.receive_host == ''
    assert cloud.receive_port == 0

def test_create_receive(no_modem):
    cloud = Cloud(None, receive_host = '127.0.0.1', receive_port = 9999)

    assert cloud.send_host == ''
    assert cloud.send_port == 0
    assert cloud.receive_host == '127.0.0.1'
    assert cloud.receive_port == 9999

def test_invalid_send_message(no_modem):
    cloud = Cloud(None, receive_host = '127.0.0.1', receive_port = 9999)

    with pytest.raises(Exception, match = 'Must instantiate a Cloud type'):
        cloud.sendMessage("hello SMS")

def test_invalid_send_sms(no_modem):
    cloud = Cloud(None, send_host = '127.0.0.1', send_port = 9999)

    with pytest.raises(Exception, match = 'Must instantiate a Cloud type'):
        cloud.sendSMS('+12345678900', 'hello SMS')

# This is good for testing if we updated the internal SDK version numbers before release.
def test_sdk_version(no_modem):
    cloud = Cloud(None, send_host = '127.0.0.1', send_port = 9999)

    assert cloud.version == '0.9.0'
