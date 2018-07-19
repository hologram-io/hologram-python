#!/usr/bin/env python

# hologram_receive.py - Hologram Python SDK command line interface (CLI) for inbound messages.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License

from Hologram.HologramCloud import HologramCloud
from hologram_util import handle_polling
from hologram_util import VAction
import sys

help_data = '''This subcommand allows you to listen on a given host and port for incoming cloud messages.\n
'''

help_sms = '''This subcommand allows you to listen on a given host and port for incoming SMS.\n
'''

hologram = None

def popReceivedMessage():
    recv = hologram.popReceivedMessage()
    if recv is not None:
        print 'Received message: ' + str(recv)

def popReceivedSMS():
    recv = hologram.popReceivedSMS()
    if recv is not None:
        print 'Received SMS:', recv


def parse_common_receive_args(parser):
    parser.add_argument('-m', '--modem', nargs='?', default='nova',
                        help='The modem type. Choose between nova, ms2131 and e303.')
    parser.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)
    parser.add_argument('-t', '--timeout', type=int, nargs='?', default=-1,
                        help='The number of seconds before the socket is closed. Default is to block indefinitely.')


def parse_hologram_receive_args(parser):
    parse_common_receive_args(parser)
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
    hologram = HologramCloud(dict(), network='cellular')

    hologram.event.subscribe('message.received', popReceivedMessage)

    if not hologram.network.at_sockets_available:
        hologram.network.connect()

    try:
        hologram.openReceiveSocket()
    except Exception as e:
        print("Failed to open socket to listen for data: %s"%str(e))
        return

    print ('Ready to receive data on port %s' % hologram.receive_port)

    try:
        handle_polling(args['timeout'], popReceivedMessage, 1)
    except KeyboardInterrupt as e:
        pass

    print 'Closing socket...'
    hologram.closeReceiveSocket()

    if not hologram.network.at_sockets_available:
        hologram.network.disconnect()

# EFFECTS: Receives SMS from the Hologram Cloud.
def run_hologram_receive_sms(args):
    global hologram
    hologram = HologramCloud(dict(), network='cellular')
    print ('Ready to receive sms')
    try:
        handle_polling(args['timeout'], popReceivedSMS, 1)
    except KeyboardInterrupt as e:
        sys.exit(e)
