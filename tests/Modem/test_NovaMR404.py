# Author: Hologram <support@hologram.io>
#
# Copyright 2017 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_NovaMR404.py - This file implements unit tests for the NovaM_R404 modem interface.

from mock import patch
import pytest
import sys

from Hologram.Network.Modem.NovaM_R404 import NovaM_R404

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
    monkeypatch.setattr(NovaM_R404, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(NovaM_R404, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(NovaM_R404, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(NovaM_R404, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(NovaM_R404, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(NovaM_R404, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_novam404_no_args(no_serial_port):
    modem = NovaM_R404()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script') == True)
    assert(modem._at_sockets_available == True)
    assert(modem.description == 'Hologram Nova US 4G LTE Cat-M1 Cellular USB Modem (R404)')

def test_disable_at_sockets_mode(no_serial_port):
    modem = NovaM_R404()
    assert(modem._at_sockets_available == True)
    modem.disable_at_sockets_mode()
    assert(modem._at_sockets_available == False)

@patch.object(NovaM_R404, 'check_registered')
def test_is_registered(mock_check_registered, no_serial_port):
    modem = NovaM_R404()
    mock_check_registered.return_value = True
    mock_check_registered.reset_mock()
    assert(modem.is_registered() == True)
    mock_check_registered.assert_called_once_with('+CEREG')

@patch.object(NovaM_R404, 'set')
def test_close_socket_no_args(mock_set, no_serial_port):
    modem = NovaM_R404()
    assert(modem.socket_identifier == 0)
    mock_set.return_value = (0,0)
    mock_set.reset_mock()
    modem.close_socket()
    mock_set.assert_called_once_with('+USOCL', '0', timeout=40)

@patch.object(NovaM_R404, 'set')
def test_close_socket_with_socket_identifier(mock_set, no_serial_port):
    modem = NovaM_R404()
    mock_set.return_value = (0,0)
    mock_set.reset_mock()
    modem.close_socket(5)
    mock_set.assert_called_once_with('+USOCL', '5', timeout=40)

@patch.object(NovaM_R404, 'command')
def test_set_network_registration_status(mock_command, no_serial_port):
    modem = NovaM_R404()
    mock_command.return_value = []
    mock_command.reset_mock()
    modem.set_network_registration_status()
    mock_command.assert_called_once_with('+CEREG', '2')
