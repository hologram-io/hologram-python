#!/usr/bin/env python

# hologram_spacebridge.py - Hologram Python SDK command line interface (CLI) for
#                           spacebridge interfaces
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

from Hologram.HologramCloud import HologramCloud
from Hologram.Network import NetworkScope
from hologram_util import handle_polling
from scripts.hologram_receive import parse_common_receive_args
import sys

# pylint: disable=W0603
hologram = None


def popReceivedMessage():
    recv = hologram.popReceivedMessage()
    if recv is not None:
        print('Received message: ' + str(recv))


def parse_hologram_spacebridge_args(parser):
    parse_common_receive_args(parser)
    parser.set_defaults(command_selected='spacebridge')


def run_hologram_spacebridge(args):
    global hologram
    hologram = HologramCloud(dict(), network='cellular')

    hologram.event.subscribe('message.received', popReceivedMessage)

    hologram.network.disable_at_sockets_mode()  # Persistent cellular connection
    hologram.network.scope = NetworkScope.HOLOGRAM  # Default route NOT set to cellular
    hologram.network.connect()

    hologram.openReceiveSocket()
    print ('Ready to receive data on port %s' % hologram.receive_port)

    try:
        handle_polling(args['timeout'], popReceivedMessage, 1)
    except KeyboardInterrupt as e:
        print('Closing socket...')
        hologram.closeReceiveSocket()
        sys.exit(e)
    finally:
        hologram.network.disconnect()
