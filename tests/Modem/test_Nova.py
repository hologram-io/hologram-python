# Author: Hologram <support@hologram.io>
#
# Copyright 2017 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Nova.py - This file implements unit tests for the Nova modem interface.

import pytest
import sys

from Hologram.Network.Modem.Nova import Nova

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")

def mock_write(nova, message):
    return True

def mock_read(nova):
    return True

def mock_readline(nova, timeout=None, hide=False):
    return ''

def mock_open_serial_port(nova, device_name=None):
    return True

def mock_close_serial_port(nova):
    return True

def mock_detect_usable_serial_port(nova, stop_on_first=True):
    return '/dev/ttyUSB0'

@pytest.fixture
def no_serial_port(monkeypatch):
    monkeypatch.setattr(Nova, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(Nova, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(Nova, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(Nova, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(Nova, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(Nova, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_nova_no_args(no_serial_port):
    modem = Nova()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script') == True)
    assert(modem._at_sockets_available == False)

def test_init_nova_chatscriptfileoverride(no_serial_port):
    modem = Nova(chatscript_file='test-chatscript')
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file == 'test-chatscript')
