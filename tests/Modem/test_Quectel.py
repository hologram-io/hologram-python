# Author: Hologram <support@hologram.io>
#
# Copyright 2017 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Quectel.py - This file implements unit tests for the Quectel modem interface.

from unittest.mock import patch
import pytest
import sys

from Hologram.Network.Modem.Quectel import Quectel
from UtilClasses import ModemResult

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
    monkeypatch.setattr(Quectel, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(Quectel, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(Quectel, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(Quectel, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(Quectel, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(Quectel, 'detect_usable_serial_port', mock_detect_usable_serial_port)

def test_init_Quectel_no_args(no_serial_port):
    modem = Quectel()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script'))
    assert(modem._at_sockets_available)

@patch.object(Quectel, 'command')
def test_connect_socket(mock_command, no_serial_port):
    modem = Quectel()
    modem.socket_identifier = 1
    host = 'hologram.io'
    port = 9999
    modem.connect_socket(host, port)
    mock_command.assert_called_with('+QIOPEN', '1,0,\"TCP\",\"%s\",%d,0,1' % (host, port))

@patch.object(Quectel, 'set')
def test_write_socket_small(mock_command, no_serial_port):
    modem = Quectel()
    modem.socket_identifier = 1
    data = b'Message smaller than 510 bytes'
    modem.write_socket(data)
    mock_command.assert_called_with('+QISENDEX', '1,"4d65737361676520736d616c6c6572207468616e20353130206279746573"')

@patch.object(Quectel, 'set')
def test_write_socket_large(mock_command, no_serial_port):
    modem = Quectel()
    modem.socket_identifier = 1
    data = b'a'*300
    modem.write_socket(data)
    mock_command.assert_called_with('+QISENDEX', '1,\"%s\"' % ('61'*255))
    mock_command.assert_called_with('+QISENDEX', '1,\"%s\"' % ('61'*45))