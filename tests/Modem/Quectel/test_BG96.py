# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_BG96.py - This file implements unit tests for the BG96 modem interface.

from mock import patch
import pytest
import sys

from Hologram.Modem.Quectel.BG96 import BG96

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")

def mock_write(bg96, message):
    return True

def mock_read(bg96):
    return True

def mock_readline(bg96, timeout=None, hide=False):
    return ''

def mock_open_serial_port(bg96, device_name=None):
    return True

def mock_close_serial_port(bg96):
    return True

def mock_detect_usable_serial_port(bg96, stop_on_first=True):
    return '/dev/ttyUSB0'

@pytest.fixture
def no_serial_port(monkeypatch):
    monkeypatch.setattr(BG96, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(BG96, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(BG96, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(BG96, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(BG96, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(BG96, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_bg96_no_args(no_serial_port):
    modem = BG96()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script'))
    assert(modem._at_sockets_available == False)

def test_init_bg96_chatscriptfileoverride(no_serial_port):
    modem = BG96(chatscript_file='test-chatscript')
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file == 'test-chatscript')

@patch.object(BG96, 'command')
def test_disable_at_sockets_mode_bg96(mock_command, no_serial_port):
    modem = BG96()

    mock_command.return_value = []
    mock_command.reset_mock()
    modem.disable_at_sockets_mode()
    # The disable_at_sockets_mode() call should not do anything.
    mock_command.assert_not_called()
