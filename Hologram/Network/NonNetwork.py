# NonNetwork.py - Hologram Python SDK Non Network interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from ..Event import Event

class NonNetwork(object):

    def __init__(self):
        self.event = Event()
        self.event.broadcast('network.connected')
