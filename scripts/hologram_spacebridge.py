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
from scripts.hologram_receive import run_hologram_receive

def parse_hologram_spacebridge_args(parser):
    parser.set_defaults(command_selected='spacebridge')
    parser.add_argument('-m', '--modem', nargs='?', default='iota',
                        help='The modem type. Choose between iota, ms2131 and e303.')
    parser.add_argument('--devicekey', nargs='?', required=True,
                        help='Hologram device key (8 characters long)')
    parser.add_argument('-f', '--file', nargs='?',
                        help='Configuration (HJSON) file that stores the required \
                              credentials to send the message to the cloud')
    parser.add_argument('-v', '--verbose', action='store_true', required=False)
    parser.add_argument('-t', '--timeout', type=int, nargs='?', default=-1,
                        help='The number of seconds before the socket is closed. \
                              Default is to block indefinitely.')

def run_hologram_spacebridge(args):
    args['command_selected'] = 'receive_data'
    run_hologram_receive(args)
