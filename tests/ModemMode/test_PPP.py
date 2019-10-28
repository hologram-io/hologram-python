# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_PPP.py - This file implements unit tests for the PPP class.

import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem.ModemMode.MockPPP import MockPPP

class TestPPP():

    def test_ppp_create(self):
        ppp = MockPPP(chatscript_file='test')

        assert ppp.device_name == '/dev/ttyUSB0'
        assert ppp.baud_rate == '9600'
        assert ppp.localIPAddress is None
        assert ppp.remoteIPAddress is None
        assert ppp.connect_script == '/usr/sbin/chat -v -f test'

    def test_ppp_invalid_chatscript_create(self):
        with pytest.raises(Exception, match='Must specify chatscript file'):
            ppp = MockPPP()
