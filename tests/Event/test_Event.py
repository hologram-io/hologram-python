# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# test_Event.py - This file implements unit tests for the
#                                Event class.

import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Event import Event

class TestEvent(object):

    def test_create(self):
        event = Event()
