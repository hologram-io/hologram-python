#!/usr/bin/env python

# hologram_send.py - Hologram Python SDK command line interface (CLI) for sending messages to the cloud
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

import argparse
import time
from Hologram.CustomCloud import CustomCloud
from Hologram.HologramCloud import HologramCloud

DEFAULT_TIMEOUT = 5

help_cloud = '''
This subcommand allows you to send cloud messages to the Hologram Cloud.
'''

help_sms = '''
This subcommand allows you to send SMS to a specified destination number.
'''
# EFFECTS: Parses hologram send CLI options.
def parse_hologram_send_args(parser):
    # Create a subparser
    subparsers = parser.add_subparsers(title='subcommands')

    # $ hologram send cloud ...
    parse_cloud_args(subparsers)

    # $ hologram send sms ...
    parse_sms_args(subparsers)

# EFFECTS: Parses the send cloud options. Sets the default command_selected option
#          to send_cloud.
def parse_cloud_args(subparsers):
    parser = subparsers.add_parser('cloud', help=help_cloud)
    parser.set_defaults(command_selected='send_cloud')

    parser.add_argument('message', nargs='?', help='Message that will be sent to the cloud')
    parser.add_argument('--authtype', default='csrpsk', nargs='?',
                        help='The authentication type used if HologramCloud is in use')
    parser.add_argument('--duration', type=int, nargs='?', default=-1,
                        help='The number of seconds before periodic message ends. \
                              Default is to block indefinitely.')
    parser.add_argument('--devicekey', nargs='?', help='Hologram device key (8 characters long)')
    parser.add_argument('--iccid', nargs='?', help='Hologram device id')
    parser.add_argument('--imsi', nargs='?', help='Hologram private key')
    parser.add_argument('--repeat', type=int, default=0, nargs='?',
                        help='Time period for each message send')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, nargs='?',
                              help='The period in seconds before the socket closes \
                                if it doesn\'t receive a response')
    parser.add_argument('--host', required=False, help=argparse.SUPPRESS)
    parser.add_argument('-p', '--port', type=int, required=False,
                        help=argparse.SUPPRESS)
    parser.add_argument('-t', '--topic', nargs = '*',
                              help='Topics for the message (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', required=False)

# EFFECTS: Parses the send sms options. Sets the default command_selected option
#          to send_sms.
def parse_sms_args(subparsers):
    parser = subparsers.add_parser('sms', help=help_sms)
    parser.set_defaults(command_selected='send_sms')

    parser.add_argument('message', nargs='?', help='Message that will be sent to the cloud')
    parser.add_argument('--devicekey', nargs = '?', required=True,
                        help = 'Hologram device key (8 characters long)')
    parser.add_argument('--destination', nargs = '?', required=True,
                        help = 'The destination number in which the SMS will be sent')

# EFFECTS: Parses and sends the Hologram message using TOTP Authentication
def sendTOTP(args, data):

    if not args['iccid'] and ('device_id' in data):
        args['iccid'] = data['device_id']

    if not args['imsi'] and ('private_key' in data):
        args['imsi'] = data['private_key']

    credentials = {'device_id': args['iccid'], 'private_key': args['imsi']}
    hologram = HologramCloud(credentials, enable_inbound=False,
                             authentication_type=args['authtype'],
                             network='cellular')

    modem = ''
    # Load the ICCID and IMSI values if modem is physically attached to machine
    if hologram.network.isModemAttached():
        modem = hologram.network.active_modem_interface
        hologram.credentials = {'device_id': hologram.network.iccid,
                                'private_key': hologram.network.imsi}
        hologram.initializeNetwork('cellular-' + str(modem).lower())

    if (hologram.credentials['device_id'] is None) or (hologram.credentials['private_key'] is None):
        raise Exception('Device id or private key not specified')

    result = hologram.network.connect()
    if result == False:
        raise Exception('Failed to connect to cell network')

    send_message_helper(hologram, args)
    hologram.network.disconnect()

# EFFECTS: Parses and sends the specified message using CSRPSK Authentication
def sendPSK(args, data):

    if not (args['devicekey']) and ('devicekey' in data):
        args['devicekey'] = data['devicekey']

    if not args['devicekey']:
        raise Exception('Device key not specified')

    credentials = {'devicekey': args['devicekey']}

    recv = ''
    if args['host'] or args['port']:
        # we're using some custom cloud
        customCloud = CustomCloud(None,
                                  send_host=args['host'],
                                  send_port=args['port'])
        recv = customCloud.sendMessage(args['message'], timeout=args['timeout'])
        print 'RESPONSE FROM CLOUD: ' + str(recv)
    else:
        # host and port are default so use Hologram
        hologram = HologramCloud(credentials, authentication_type=args['authtype'])
        send_message_helper(hologram, args)

# EFFECTS: Wraps the send message interface based on the repeat parameter.
def send_message_helper(cloud, args):

    if args['repeat'] == 0:
        recv = cloud.sendMessage(args['message'], topics=args['topic'],
                                 timeout=args['timeout'])
        print 'RESPONSE CODE FROM CLOUD: ' + str(recv)
        print 'RESPONSE MESSAGE: ' + cloud.getResultString(recv)
    else:
        cloud.sendPeriodicMessage(args['repeat'],
                                  args['message'],
                                  topics=args['topic'],
                                  timeout=args['timeout'])
        keep_periodic_msg_alive(args['duration'])

def keep_periodic_msg_alive(duration):
    if duration != -1:
        print 'waiting for ' + str(duration) + ' seconds...'
        time.sleep(duration)
    else:
        while True:
            time.sleep(1)

# EFFECTS: Handles all hologram_send operations.
#          This function will call the appropriate cloud/sms handler.
def run_hologram_send(args):

    if args['message'] is None:
        raise Exception('Message body cannot be empty')

    if args['command_selected'] == 'send_cloud':
        run_hologram_send_cloud(args)
    elif args['command_selected'] == 'send_sms':
        run_hologram_send_sms(args)
    else:
        raise Exception('Internal CLI error: Invalid command_selected value')

# EFFECTS: Sends a given Hologram message to the cloud.
def run_hologram_send_cloud(args):
    data = dict()
    if args['authtype'] == 'totp':
        sendTOTP(args, data)
    else:
        sendPSK(args, data)

# EFFECTS: Handles and sends a SMS to a specified destination number.
def run_hologram_send_sms(args):

    if not args['message']:
        raise Exception('A SMS message body must be provided')
    elif not args['destination']:
        raise Exception('A destination number must be provided in order to send SMS to it')

    credentials = {'devicekey': args['devicekey']}

    hologram = HologramCloud(credentials)
    recv = hologram.sendSMS(args['destination'], args['message']) # Send SMS to destination number
    print 'RESPONSE CODE FROM CLOUD: ' + str(recv)
    print 'RESPONSE MESSAGE: ' + hologram.getResultString(recv)
