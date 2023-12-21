# Author: Hologram <support@hologram.io>
#
# Copyright 2017 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Quectel.py - This file implements unit tests for the Quectel modem interface.

from unittest.mock import patch, call
import pytest
import sys

from Hologram.Network.Modem.Quectel import Quectel
from Hologram.Network.Modem.Modem import Modem
from UtilClasses import ModemResult

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")


def mock_write(modem, message):
    return True


def mock_read(modem):
    return True


def mock_readline(modem, timeout=None, hide=False):
    return ""


def mock_open_serial_port(modem, device_name=None):
    return True


def mock_close_serial_port(modem):
    return True


def mock_detect_usable_serial_port(modem, stop_on_first=True):
    return "/dev/ttyUSB0"


@pytest.fixture
def no_serial_port(monkeypatch):
    monkeypatch.setattr(Quectel, "_read_from_serial_port", mock_read)
    monkeypatch.setattr(Quectel, "_readline_from_serial_port", mock_readline)
    monkeypatch.setattr(Quectel, "_write_to_serial_port_and_flush", mock_write)
    monkeypatch.setattr(Quectel, "openSerialPort", mock_open_serial_port)
    monkeypatch.setattr(Quectel, "closeSerialPort", mock_close_serial_port)
    monkeypatch.setattr(Quectel, "detect_usable_serial_port", mock_detect_usable_serial_port)


def test_init_Quectel_no_args(no_serial_port):
    modem = Quectel()
    assert modem.timeout == 1
    assert modem.socket_identifier == 0
    assert modem.chatscript_file.endswith("/chatscripts/default-script")
    assert modem._at_sockets_available

@patch.object(Quectel, "check_registered")
@patch.object(Quectel, "set")
@patch.object(Quectel, "command")
def test_create_socket(mock_command, mock_set, mock_check, no_serial_port):
    modem = Quectel()
    modem.apn = 'test'
    mock_check.return_value = True
    # The PDP context is not active
    mock_command.return_value = (ModemResult.OK, '+QIACT: 0,0')
    mock_set.return_value = (ModemResult.OK, None)
    modem.create_socket()
    mock_command.assert_called_with("+QIACT?")
    mock_set.assert_has_calls(
        [
            call("+QICSGP", '1,1,\"test\",\"\",\"\",1'),
            call("+QIACT", '1', timeout=30)
        ],
        any_order=True
    )

@patch.object(Quectel, "command")
def test_connect_socket(mock_command, no_serial_port):
    modem = Quectel()
    modem.socket_identifier = 1
    host = "hologram.io"
    port = 9999
    modem.connect_socket(host, port)
    mock_command.assert_called_with("+QIOPEN", '1,0,"TCP","%s",%d,0,1' % (host, port))


@patch.object(Quectel, "set")
def test_write_socket_small(mock_command, no_serial_port):
    modem = Quectel()
    modem.socket_identifier = 1
    data = b"Message smaller than 510 bytes"
    mock_command.return_value = (ModemResult.OK, None)
    modem.write_socket(data)
    mock_command.assert_called_with(
        "+QISENDEX",
        '1,"4d65737361676520736d616c6c6572207468616e20353130206279746573"',
        timeout=10,
    )


@patch.object(Quectel, "set")
def test_write_socket_large(mock_command, no_serial_port):
    modem = Quectel()
    modem.socket_identifier = 1
    data = b"a" * 300
    mock_command.return_value = (ModemResult.OK, None)
    modem.write_socket(data)
    mock_command.assert_has_calls(
        [
            call("+QISENDEX", '1,"%s"' % ("61" * 255), timeout=10),
            call("+QISENDEX", '1,"%s"' % ("61" * 45), timeout=10),
        ],
        any_order=True,
    )

@patch.object(Quectel, "set")
def test_read_socket(mock_command, no_serial_port):
    modem = Quectel()
    modem.socket_identifier = 1
    mock_command.return_value = (ModemResult.OK, '+QIRD: "Some val"')
    # Double quotes should be stripped from the reutrn value
    assert (modem.read_socket(payload_length=10) == 'Some val')
    mock_command.assert_called_with("+QIRD", '1,10')

def test_handle_open_urc(no_serial_port):
    modem = Quectel()
    modem.handleURC('+QIOPEN: 1,0')
    assert modem.urc_state == Modem.SOCKET_WRITE_STATE
    assert modem.socket_identifier == 1

def test_handle_received_data_urc(no_serial_port):
    modem = Quectel()
    modem.handleURC('+QIURC: \"recv\",1,25')
    assert modem.urc_state == Modem.SOCKET_SEND_READ
    assert modem.socket_identifier == 1
    assert modem.last_read_payload_length == 25
    assert modem.urc_response == ""

def test_handle_socket_closed_urc(no_serial_port):
    modem = Quectel()
    modem.handleURC('+QIURC: \"closed\",1')
    assert modem.urc_state == Modem.SOCKET_CLOSED
    assert modem.socket_identifier == 1

