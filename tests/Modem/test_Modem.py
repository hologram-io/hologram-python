# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Modem.py - This file implements unit tests for the Modem class.

import pytest
import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Exceptions.HologramError import SerialError
from Hologram.Network.Modem.Modem import Modem
from UtilClasses import ModemResult

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
    monkeypatch.setattr(Modem, '_read_from_serial_port', mock_read)
    monkeypatch.setattr(Modem, '_readline_from_serial_port', mock_readline)
    monkeypatch.setattr(Modem, '_write_to_serial_port_and_flush', mock_write)
    monkeypatch.setattr(Modem, 'openSerialPort', mock_open_serial_port)
    monkeypatch.setattr(Modem, 'closeSerialPort', mock_close_serial_port)
    monkeypatch.setattr(Modem, 'detect_usable_serial_port', mock_detect_usable_serial_port)


# CONSTRUCTOR


def test_init_modem_no_args(no_serial_port):
    modem = Modem()
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file.endswith('/chatscripts/default-script') == True)
    assert(modem._at_sockets_available == False)
    assert(modem.description == 'Modem')

def test_init_modem_chatscriptfileoverride(no_serial_port):
    modem = Modem(chatscript_file='test-chatscript')
    assert(modem.timeout == 1)
    assert(modem.socket_identifier == 0)
    assert(modem.chatscript_file == 'test-chatscript')

def test_get_result_string(no_serial_port):
    modem = Modem()
    assert(modem.getResultString(0) == 'Modem returned OK')
    assert(modem.getResultString(-1) == 'Modem timeout')
    assert(modem.getResultString(-2) == 'Modem error')
    assert(modem.getResultString(-3) == 'Modem response doesn\'t match expected return value')
    assert(modem.getResultString(-99) == 'Unknown response code')


# PROPERTIES


def test_get_location(no_serial_port):
    modem = Modem()
    with pytest.raises(NotImplementedError) as e:
        assert(modem.location == 'test location')
    assert('This modem does not support this property' in e.value)


# DEBUGWRITE


def test_debugwrite(no_serial_port):
    modem = Modem()
    assert(modem.debug_out == '')
    modem.debugwrite('test')
    assert(modem.debug_out == 'test')

    modem.debugwrite('test222', hide=True)
    assert(modem.debug_out == 'test') # debug_out shouldn't change since hide is enabled.


# MODEMWRITE


def test_modemwrite(no_serial_port):
    modem = Modem()
    assert(modem.debug_out == '')

    # use all method arg default values.
    modem.modemwrite('test-cmd')
    assert(modem.debug_out == 'test-cmd')

    modem.modemwrite('test2', start=True)
    assert(modem.debug_out == '[test2')

    modem.modemwrite('test3', start=True, hide=True)
    # This should be the same as the previous debug_out because hide is enabled.
    assert(modem.debug_out == '[test2')

    modem.modemwrite('test4', start=True, end=True)
    assert(modem.debug_out == '[test4]')

    modem.modemwrite('test5', start=True, at=True, seteq=True, read=True, end=True)
    assert(modem.debug_out == '[ATtest5=?]')


# COMMAND_RESULT

def test_command_result(no_serial_port):

    modem = Modem()

    # OK with an empty response list.
    assert(modem.result == ModemResult.OK)
    result, resp = modem._command_result()

    assert(result == ModemResult.OK)
    assert(resp == [])

    # OK with a response list of one element.
    modem.result = ModemResult.OK
    modem.response = ['test1']
    result, resp = modem._command_result()

    assert(result == ModemResult.OK)
    assert(resp == 'test1') # should return just a string

    # INVALID
    modem.result = ModemResult.Invalid
    modem.response = ['test1', 'test2', 'test3']

    result, resp = modem._command_result()

    assert(result == ModemResult.Invalid)
    assert(resp == ['test1', 'test2', 'test3'])

    # NOMATCH
    modem.result = ModemResult.NoMatch
    # This should still be a list since it's not ModemResult.OK.
    modem.response = ['test1']
    result, resp = modem._command_result()

    assert(result == ModemResult.NoMatch)
    assert(resp == ['test1'])

    # ERROR
    modem.result = ModemResult.Error
    modem.response = []
    result, resp = modem._command_result()

    assert(result == ModemResult.Error)
    assert(resp == [])

    # TIMEOUT
    modem.result = ModemResult.Timeout
    result, resp = modem._command_result()

    assert(result == ModemResult.Timeout)
    assert(resp == [])

# HANDLEURC


# These are static methods that can be tested independently.
# We decided to wrap it all here under this test object
class TestModemProtectedStaticMethods(object):

    def test_check_registered_string(self):
        result = '+CREG: 2,5,"5585","404C790",6'
        registered = Modem._check_registered_helper('+CREG', result)
        assert(registered == True)

    def test_registered_basic_unregistered_string(self):
        # This should force strips left and right, but the return value will
        # still be false since 3 is elem 1 in [2, 3, 2]
        result = '2, 3, 2'
        registered = Modem._check_registered_helper('+CREG', result)
        assert(registered == False)

    def test_registered_empty_string(self):
        result = ''
        with pytest.raises(SerialError) as e:
            registered = Modem._check_registered_helper('+CREG', result)

    def test_check_registered_short_list(self):
        result = ['+CREG: 5,"5585","404C78A",6',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 2,5,"5585","404C790",6']
        registered = Modem._check_registered_helper('+CREG', result)
        assert(registered == True)

    def test_registered_empty_list(self):
        result = []
        with pytest.raises(SerialError) as e:
            registered = Modem._check_registered_helper('+CREG', result)

    def test_check_registered_long_list(self):
        result = ['+CREG: 5,"5585","404EF4D",6',
                  '+CREG: 5,"5585","404C816",6',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 5,"5585","404C816",6',
                  '+CREG: 5,"5585","404EF4D",6',
                  '+CREG: 5,"5585","404C78A",6',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 5,"5585","404C816",6',
                  '+CREG: 2',
                  '+CREG: 5,"5585","404C790",6',
                  '+CREG: 2,5,"5585","404C790",6']
        registered = Modem._check_registered_helper('+CREG', result)
        assert(registered == True)
