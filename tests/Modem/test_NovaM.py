# Author: Hologram <support@hologram.io>
#
# Copyright 2018 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_NovaM.py - This file implements unit tests for the NovaM modem interface.

from mock import patch
import pytest
import sys

from Hologram.Network.Modem.NovaM import NovaM

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
    monkeypatch.setattr(NovaM, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(NovaM, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(NovaM, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(NovaM, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(NovaM, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(NovaM, 'detect_usable_serial_port', mock_detect_usable_serial_port)
    monkeypatch.setattr(NovaM, 'modem_id', 'Sara-R410M-02B')

def test_init_novam_no_args(no_serial_port):
    modem = NovaM()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script') == True)
    assert(modem._at_sockets_available == True)
    assert(modem.description == 'Hologram Nova US 4G LTE Cat-M1 Cellular USB Modem (R410)')

def test_disable_at_sockets_mode(no_serial_port):
    modem = NovaM()
    assert(modem._at_sockets_available == True)
    modem.disable_at_sockets_mode()
    assert(modem._at_sockets_available == False)

@patch.object(NovaM, 'check_registered')
def test_is_registered(mock_check_registered, no_serial_port):
    modem = NovaM()
    mock_check_registered.return_value = True
    mock_check_registered.reset_mock()
    assert(modem.is_registered() == True)
    mock_check_registered.assert_called_once_with('+CEREG')

@patch.object(NovaM, 'set')
def test_close_socket_no_args(mock_set, no_serial_port):
    modem = NovaM()
    assert(modem.socket_identifier == 0)
    mock_set.return_value = (0,0)
    mock_set.reset_mock()
    modem.close_socket()
    mock_set.assert_called_once_with('+USOCL', '0', timeout=40)

@patch.object(NovaM, 'set')
def test_close_socket_with_socket_identifier(mock_set, no_serial_port):
    modem = NovaM()
    mock_set.return_value = (0,0)
    mock_set.reset_mock()
    modem.close_socket(5)
    mock_set.assert_called_once_with('+USOCL', '5', timeout=40)

@patch.object(NovaM, 'command')
def test_set_network_registration_status(mock_command, no_serial_port):
    modem = NovaM()
    mock_command.return_value = []
    mock_command.reset_mock()
    modem.set_network_registration_status()
    mock_command.assert_called_once_with('+CEREG', '2')
