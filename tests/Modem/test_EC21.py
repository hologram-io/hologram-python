# Author: Hologram <support@hologram.io>
#
# Copyright 2017 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_EC21.py - This file implements unit tests for the EC21 modem interface.

from mock import call, patch
import pytest
import sys

from Hologram.Network.Modem.EC21 import EC21

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")

def mock_write(modem, message):
    return True

def mock_read(modem):
    return True

def mock_readline(modem, timeout=None, hide=False):
    return ''

def mock_open_serial_port(modem, device_name=None):
    return True

def mock_close_serial_port(modem):
    return True

def mock_detect_usable_serial_port(modem, stop_on_first=True):
    return '/dev/ttyUSB0'

@pytest.fixture
def no_serial_port(monkeypatch):
    monkeypatch.setattr(EC21, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(EC21, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(EC21, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(EC21, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(EC21, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(EC21, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_EC21_no_args(no_serial_port):
    modem = EC21()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script'))
    assert(modem._at_sockets_available)

@patch.object(EC21, 'check_registered')
def test_is_registered(mock_check_registered, no_serial_port):
    modem = EC21()
    mock_check_registered.return_value = False
    mock_check_registered.reset_mock()
    assert(modem.is_registered() == False)
    calls = [call('+CREG'), call('+CEREG')]
    mock_check_registered.assert_has_calls(calls, any_order=True)

@patch.object(EC21, 'command')
def test_set_network_registration_status(mock_command, no_serial_port):
    modem = EC21()
    mock_command.return_value = []
    mock_command.reset_mock()
    modem.set_network_registration_status()
    calls = [call('+CREG', '2'), call('+CEREG', '2')]
    mock_command.assert_has_calls(calls)
