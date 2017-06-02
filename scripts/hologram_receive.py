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

hologram = None

def popReceivedMessage():
    recv = hologram.popReceivedMessage()
    print 'Received message: ' + str(recv)

def popReceivedSMS():
    recv = hologram.popReceivedSMS()
    print 'Received SMS: ' + str(recv)

def parse_hologram_receive_args(parser):
    parser.add_argument('-m', '--modem', nargs='?', default='iota',
                        help='The modem type. Choose between iota, ms2131 and e303.')
    parser.add_argument('-v', '--verbose', action='store_true', required=False)
    parser.add_argument('-t', '--timeout', type=int, nargs='?', default=-1,
                        help='The number of seconds before the socket is closed. \
                              Default is to block indefinitely.')
    parse_data_args(parser)
    parse_sms_args(parser)

def parse_data_args(parser):
    parser.set_defaults(command_selected='receive_data')
    parser.add_argument('--data', action='store_true', required=False)

def parse_sms_args(parser):
    parser.set_defaults(command_selected='receive_sms')
    parser.add_argument('--sms', action='store_true', required=False)

def run_hologram_receive(args):

    if args['data'] and args['sms']:
        raise Exception('must pick either one of data or sms')
    if args['sms']:
        run_hologram_receive_sms(args)
    else:
        run_hologram_receive_data(args)

# EFFECTS: Receives data from the Hologram Cloud.
def run_hologram_receive_data(args):

    global hologram
    hologram = HologramCloud(None, enable_inbound=False,
                             network='cellular-' + str(args['modem']))

    hologram.event.subscribe('message.received', popReceivedMessage)
    result = hologram.network.connect()
    if result == False:
        print 'Failed to connect to cell network'

    print 'Listening to port ' + str(hologram.receive_port)
    hologram.initializeReceiveSocket()

    handle_timeout(args['timeout'])

    hologram.closeReceiveSocket()

    hologram.network.disconnect()

# EFFECTS: Receives SMS from the Hologram Cloud.
def run_hologram_receive_sms(args):

    global hologram
    hologram = HologramCloud(None, enable_inbound=False, network='cellular-iota')

    hologram.event.subscribe('sms.received', popReceivedSMS)
    hologram.enableSMS()

    handle_timeout(args['timeout'])

    hologram.disableSMS()
