# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_ModemMode.py - This file implements unit tests for the ModemMode class.

import sys
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode.ModemMode import ModemMode

class TestModemMode(object):

    def test_modem_mode_create(self):
        modem_mode = ModemMode(device_name='/dev/ttyUSB0', baud_rate='9600')

        assert modem_mode.device_name == '/dev/ttyUSB0'
        assert modem_mode.baud_rate == '9600'
