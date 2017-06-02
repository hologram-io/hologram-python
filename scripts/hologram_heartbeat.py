#!/usr/bin/env python

# hologram_heartbeat.py - Hologram Python SDK command line interface (CLI) for
#                           heartbeat interfaces
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

DEFAULT_TIMEOUT = 5
DEFAULT_REPEAT_PERIOD = 10

# Hologram heartbeat is basically an alias for send cloud with a specified timeout.
from scripts.hologram_send import run_hologram_send
from scripts.hologram_send import parse_hologram_send_args

def parse_hologram_heartbeat_args(parser):
    parse_hologram_send_args(parser)
    parser.set_defaults(command_selected='heartbeat')

def run_hologram_heartbeat(args):
    args['host'] = None
    args['port'] = None

    if args['repeat'] == 0:
        args['repeat'] = DEFAULT_REPEAT_PERIOD

    run_hologram_send(args)
