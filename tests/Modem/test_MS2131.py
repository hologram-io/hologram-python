# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_MS2131.py - This file implements unit tests for the MS2131 modem interface.

from mock import patch
import pytest
import sys

from Hologram.Network.Modem.MS2131 import MS2131

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")

def mock_write(ms2131, message):
    return True

def mock_read(ms2131):
    return True

def mock_readline(ms2131, timeout=None, hide=False):
    return ''

def mock_open_serial_port(ms2131, device_name=None):
    return True

def mock_close_serial_port(ms2131):
    return True

def mock_detect_usable_serial_port(ms2131, stop_on_first=True):
    return '/dev/ttyUSB0'

@pytest.fixture
def no_serial_port(monkeypatch):
    monkeypatch.setattr(MS2131, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(MS2131, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(MS2131, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(MS2131, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(MS2131, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(MS2131, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_ms2131_no_args(no_serial_port):
    modem = MS2131()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script') == True)
    assert(modem._at_sockets_available == False)

def test_init_ms2131_chatscriptfileoverride(no_serial_port):
    modem = MS2131(chatscript_file='test-chatscript')
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file == 'test-chatscript')

@patch.object(MS2131, 'command')
def test_disable_at_sockets_mode_ms2131(mock_command, no_serial_port):
    modem = MS2131()

    mock_command.return_value = []
    mock_command.reset_mock()
    modem.disable_at_sockets_mode()
    # The disable_at_sockets_mode() call should not do anything.
    mock_command.assert_not_called()
