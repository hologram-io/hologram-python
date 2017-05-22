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

def parse_hologram_heartbeat_args(parser):
    parser.set_defaults(command_selected='heartbeat')

    parser.add_argument('message', nargs='?', help='Message that will be sent to the cloud')
    parser.add_argument('--authtype', default='csrpsk', nargs='?',
                        help='The authentication type used if HologramCloud is in use')
    parser.add_argument('--duration', type=int, nargs='?', default=-1,
                        help='The number of seconds before periodic message ends. \
                              Default is to block indefinitely.')
    parser.add_argument('--devicekey', nargs='?', help='Hologram device key (8 characters long)')
    parser.add_argument('--iccid', nargs='?', help='Hologram device id')
    parser.add_argument('--imsi', nargs='?', help='Hologram private key')
    parser.add_argument('--repeat', type=int, default=DEFAULT_REPEAT_PERIOD, nargs='?',
                        help='Time period for each message send')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, nargs='?',
                              help='The period in seconds before the socket closes \
                                if it doesn\'t receive a response')
    parser.add_argument('-t', '--topic', nargs = '*',
                              help='Topics for the message (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', required=False)

def run_hologram_heartbeat(args):
    args['command_selected'] = 'send_cloud'
    args['host'] = None
    args['port'] = None
    run_hologram_send(args)
