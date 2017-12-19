# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_HologramAuthentication.py - This file implements unit tests for the
#                                HologramAuthentication class.

import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Authentication.HologramAuthentication import HologramAuthentication

credentials = {'devicekey': '12345678'}

class TestHologramAuthentication(object):

    def test_create(self):
        auth = HologramAuthentication(credentials)

    def test_invalid_auth_string(self):
        auth = HologramAuthentication(credentials)
        with pytest.raises(Exception, message = 'Must instantiate a subclass of HologramAuthentication'):
            auth.buildPayloadString('test msg', 'test topic')

    def test_invalid_topic_string(self):
        auth = HologramAuthentication(credentials)
        with pytest.raises(Exception, message = 'Must instantiate a subclass of HologramAuthentication'):
            auth.buildTopicString('test topic')

    def test_invalid_msg_string(self):
        auth = HologramAuthentication(credentials)
        with pytest.raises(Exception, message = 'Must instantiate a subclass of HologramAuthentication'):
            auth.buildMessageString('test msg')

    def test_build_modem_type_id_str(self):
        auth = HologramAuthentication(credentials)

        payload = auth.build_modem_type_id_str('Nova', 'TEST_SARA-1111')
        assert payload == 'nova-TEST_SARA-1111'

        payload = auth.build_modem_type_id_str('MS2131', 'TEST_SARA-1111')
        assert payload == 'ms2131'

        payload = auth.build_modem_type_id_str('E303', 'TEST_SARA-1111')
        assert payload == 'e303'
