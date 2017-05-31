#!/usr/bin/env python

# hologram_receive.py - Hologram Python SDK command line interface (CLI) for inbound messages.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License

from Hologram.HologramCloud import HologramCloud
from hologram_util import handle_timeout

help_data = '''This subcommand allows you to listen on a given host and port for incoming cloud messages.\n
'''

help_sms = '''This subcommand allows you to listen on a given host and port for incoming SMS.\n
'''

def parse_hologram_receive_args(parser):
    # Create a subparser
    subparsers = parser.add_subparsers(title='subcommands')
    parse_data_args(subparsers)
    parse_sms_args(subparsers)

def parse_data_args(subparsers):
    parser = subparsers.add_parser('data', help=help_data)
    parser.set_defaults(command_selected='receive_data')
    parser.add_argument('-m', '--modem', nargs='?', default='iota',
                        help='The modem type. Choose between iota, ms2131 and e303.')
    parser.add_argument('-v', '--verbose', action='store_true', required=False)
    parser.add_argument('-t', '--timeout', type=int, nargs='?', default=-1,
                        help='The number of seconds before the socket is closed. \
                              Default is to block indefinitely.')

def parse_sms_args(subparsers):
    parser = subparsers.add_parser('sms', help=help_sms)
    parser.set_defaults(command_selected='receive_sms')
    parser.add_argument('-m', '--modem', nargs='?', default='iota',
                        help='The modem type. Choose between iota, ms2131 and e303.')
    parser.add_argument('-v', '--verbose', action='store_true', required=False)
    parser.add_argument('-t', '--timeout', type=int, nargs='?', default=-1,
                        help='The number of seconds before the socket is closed. \
                              Default is to block indefinitely.')

def run_hologram_receive(args):

    if args['command_selected'] == 'receive_data':
        run_hologram_receive_data(args)
    elif args['command_selected'] == 'receive_sms':
        run_hologram_receive_sms(args)
    else:
        raise Exception('Internal CLI error: Invalid command_selected value')

# EFFECTS: Receives data from the Hologram Cloud.
def run_hologram_receive_data(args):

    hologram = HologramCloud(None, enable_inbound=False,
                             network='cellular-' + str(args['modem']))

    result = hologram.network.connect()
    if result == False:
        print 'Failed to connect to cell network'

    hologram.initializeReceiveSocket()

    handle_timeout(args['timeout'])

    hologram.closeReceiveSocket()
    recv = hologram.popReceivedMessage()
    print 'Receive buffer: ' + str(recv)

    hologram.network.disconnect()

# EFFECTS: Receives SMS from the Hologram Cloud.
def run_hologram_receive_sms(args):

    hologram = HologramCloud(None, enable_inbound=False, network='cellular-iota')

    hologram.enableSMS()

    handle_timeout(args['timeout'])

    hologram.disableSMS()

    recv = hologram.popReceivedSMS()
    print 'Received SMS buffer: ' + str(recv)
