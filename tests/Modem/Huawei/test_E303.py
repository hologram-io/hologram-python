# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_E303.py - This file implements unit tests for the E303 modem interface.

from mock import patch
import pytest
import sys

from Hologram.Modem.Huawei.E303 import E303

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")

def mock_write(e303, message):
    return True

def mock_read(e303):
    return True

def mock_readline(e303, timeout=None, hide=False):
    return ''

def mock_open_serial_port(e303, device_name=None):
    return True

def mock_close_serial_port(e303):
    return True

def mock_detect_usable_serial_port(e303, stop_on_first=True):
    return '/dev/ttyUSB0'

@pytest.fixture
def no_serial_port(monkeypatch):
    monkeypatch.setattr(E303, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(E303, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(E303, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(E303, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(E303, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(E303, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_e303_no_args(no_serial_port):
    modem = E303()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script'))
    assert(modem._at_sockets_available == False)

def test_init_e303_chatscriptfileoverride(no_serial_port):
    modem = E303(chatscript_file='test-chatscript')
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file == 'test-chatscript')

@patch.object(E303, 'command')
def test_disable_at_sockets_mode_e303(mock_command, no_serial_port):
    modem = E303()

    mock_command.return_value = []
    mock_command.reset_mock()
    modem.disable_at_sockets_mode()
    # The disable_at_sockets_mode() call should not do anything.
    mock_command.assert_not_called()
