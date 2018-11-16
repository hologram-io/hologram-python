#!/usr/bin/env python

# hologram_network.py - Hologram Python SDK command line interface (CLI) for connect/disconnect interfaces.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License

from Hologram.CustomCloud import CustomCloud
from Exceptions.HologramError import HologramError
from hologram_util import VAction
import psutil

help_connect = '''This subcommand establishes a cellular connection.\n
'''

help_disconnect = '''This subcommand brings down a cellular connection.\n
'''

def run_network_connect(args):
    cloud = CustomCloud(None, network='cellular')
    cloud.network.disable_at_sockets_mode()
    res = cloud.network.connect()
    if res:
        print 'PPP session started'
    else:
        print 'Failed to start PPP'

def run_network_disconnect(args):
    print 'Checking for existing PPP sessions'
    for proc in psutil.process_iter():

        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except:
            raise HologramError('Failed to check for existing PPP sessions')

        if 'pppd' in pinfo['name']:
            print 'Found existing PPP session on pid: %s' % pinfo['pid']
            print 'Killing pid %s now' % pinfo['pid']
            psutil.Process(pinfo['pid']).terminate()

_run_handlers = {
    'network_connect': run_network_connect,
    'network_disconnect': run_network_disconnect
}

# EFFECTS: Parses the CLI arguments as options to the hologram modem subcommand.
def parse_hologram_network_args(parser):
    # Create a subparser
    subparsers = parser.add_subparsers(title='subcommands')

    # Connect
    parser_connect = subparsers.add_parser('connect', help=help_connect)
    parser_connect.set_defaults(command_selected='network_connect')
    parser_connect.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # Disconnect
    parser_disconnect = subparsers.add_parser('disconnect', help=help_disconnect)
    parser_disconnect.set_defaults(command_selected='network_disconnect')
    parser_disconnect.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

# EFFECTS: Runs the hologram modem interfaces.
def run_hologram_network(args):

    if args['command_selected'] not in _run_handlers:
        raise Exception('Internal CLI error: Invalid command_selected value')
    else:
        _run_handlers[args['command_selected']](args)
