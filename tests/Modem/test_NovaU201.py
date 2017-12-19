# Author: Hologram <support@hologram.io>
#
# Copyright 2017 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_NovaU201.py - This file implements unit tests for the Nova_U201 modem interface.

from mock import call, patch
import pytest
import sys

from Hologram.Network.Modem.Nova_U201 import Nova_U201

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
    monkeypatch.setattr(Nova_U201, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(Nova_U201, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(Nova_U201, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(Nova_U201, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(Nova_U201, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(Nova_U201, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_nova_u201_no_args(no_serial_port):
    modem = Nova_U201()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script') == True)
    assert(modem._at_sockets_available == True)
    assert(modem.description == 'Hologram Nova Global 3G/2G Cellular USB Modem (U201)')
    assert(modem.last_location == None)

def test_disable_at_sockets_mode(no_serial_port):
    modem = Nova_U201()
    assert(modem._at_sockets_available == True)
    modem.disable_at_sockets_mode()
    assert(modem._at_sockets_available == False)

@patch.object(Nova_U201, 'check_registered')
def test_is_registered(mock_check_registered, no_serial_port):
    modem = Nova_U201()
    mock_check_registered.return_value = False
    mock_check_registered.reset_mock()
    assert(modem.is_registered() == False)
    calls = [call('+CREG'), call('+CGREG')]
    mock_check_registered.assert_has_calls(calls, any_order=True)

@patch.object(Nova_U201, 'command')
def test_set_network_registration_status(mock_command, no_serial_port):
    modem = Nova_U201()
    mock_command.return_value = []
    mock_command.reset_mock()
    modem.set_network_registration_status()
    calls = [call('+CREG', '2'), call('+CGREG', '2')]
    mock_command.assert_has_calls(calls)

def test_parse_and_populate_last_sim_otp_response(no_serial_port):
    modem = Nova_U201()

    test_response = "01,\"test1\""
    modem.parse_and_populate_last_sim_otp_response(test_response)
    assert(modem.last_sim_otp_command_response == 'test1')

    # Should still strip away the last element - test3
    test_response = "01,\"test2,test3\""
    modem.parse_and_populate_last_sim_otp_response(test_response)
    assert(modem.last_sim_otp_command_response == 'test3')
