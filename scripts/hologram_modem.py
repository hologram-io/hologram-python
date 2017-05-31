#!/usr/bin/env python

# hologram_modem.py - Hologram Python SDK command line interface (CLI) for modem interfaces.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License

from Hologram.CustomCloud import CustomCloud
from hologram_util import handle_timeout
import json
import subprocess
import time

help_connect = '''This subcommand establishes a cellular connection.\n
'''

help_disconnect = '''This subcommand brings down a cellular connection.\n
'''

help_sim = '''This subcommand prints the IMSI value of the attached SIM.\n
'''

help_type = '''This subcommand prints the modem name if it is supported and attached to the device.\n
'''

help_operator = '''This subcommand prints the operator name.\n
'''

help_signal = '''This subcommand prints the RSSI signal strength values.\n
'''

help_location = '''This subcommand prints the encoded location of the modem.\n
'''

def run_modem_connect(args):
    cloud = CustomCloud(None, enable_inbound=False, network='cellular-ms2131')
    cloud.network.connect()

def run_modem_disconnect(args):
    print 'Checking for existing PPP sessions'
    out_list = subprocess.check_output(['ps', '--no-headers', '-axo',
                                        'pid,user,tty,args']).split('\n')

    # Iterate over all processes and find pppd with the specific device name we're using.
    for process in out_list:
        if 'pppd' in process:
            print 'Found existing PPP session'
            pid = process.split(' ')[1]
            kill_command = 'kill ' + str(pid)

            print 'Killing pid %s that currently have an active PPP session' % pid
            subprocess.call(kill_command, shell=True)

def run_modem_signal(args):
    cloud = CustomCloud(None, enable_inbound=False, network='cellular-ms2131')

    if args['repeat'] != 0:
        while True:
            print 'Signal strength: ' + cloud.network.signal_strength
            handle_timeout(args['repeat'])
    else:
        print 'Signal strength: ' + cloud.network.signal_strength

def run_modem_sim(args):
    cloud = CustomCloud(None, enable_inbound=False, network='cellular-ms2131')
    print 'ICCID: ' + cloud.network.iccid

def run_modem_operator(args):
    cloud = CustomCloud(None, enable_inbound=False, network='cellular-ms2131')
    print 'Operator: ' + cloud.network.operator

def run_modem_type(args):
    cloud = CustomCloud(None, enable_inbound=False, network='cellular-ms2131')
    print 'Type: ' + str(cloud.network.active_modem_interface)

def run_modem_location(args):
    cloud = CustomCloud(None, enable_inbound=False, network='cellular-ms2131')
    location_obj = cloud.network.location
    print 'Location: ' + convert_location_into_json(location_obj)

_run_handlers = {
    'modem_connect': run_modem_connect,
    'modem_disconnect': run_modem_disconnect,
    'modem_sim': run_modem_sim,
    'modem_operator': run_modem_operator,
    'modem_signal': run_modem_signal,
    'modem_type': run_modem_type,
    'modem_location': run_modem_location
}

# EFFECTS: Parses the CLI arguments as options to the hologram modem subcommand.
def parse_hologram_modem_args(parser):
    # Create a subparser
    subparsers = parser.add_subparsers(title='subcommands')

    # Connect
    parser_connect = subparsers.add_parser('connect', help=help_connect)
    parser_connect.set_defaults(command_selected='modem_connect')
    parser_connect.add_argument('-v', '--verbose', action='store_true', required=False)

    # Disconnect
    parser_disconnect = subparsers.add_parser('disconnect', help=help_disconnect)
    parser_disconnect.set_defaults(command_selected='modem_disconnect')
    parser_disconnect.add_argument('-v', '--verbose', action='store_true', required=False)

    # Signal
    parser_signal = subparsers.add_parser('signal', help=help_signal)
    parser_signal.set_defaults(command_selected='modem_signal')
    parser_signal.add_argument('--repeat', type=int, default=0, nargs='?',
                               help='Time period for each signal read')
    parser_signal.add_argument('-v', '--verbose', action='store_true', required=False)

    # Operator
    parser_operator = subparsers.add_parser('operator', help=help_operator)
    parser_operator.set_defaults(command_selected='modem_operator')
    parser_operator.add_argument('-v', '--verbose', action='store_true', required=False)

    # SIM
    parser_sim = subparsers.add_parser('sim', help=help_sim)
    parser_sim.set_defaults(command_selected='modem_sim')
    parser_sim.add_argument('-v', '--verbose', action='store_true', required=False)

    # Type
    parser_type = subparsers.add_parser('type', help=help_type)
    parser_type.set_defaults(command_selected='modem_type')
    parser_type.add_argument('-v', '--verbose', action='store_true', required=False)

    # Location
    parser_location = subparsers.add_parser('location', help=help_location)
    parser_location.set_defaults(command_selected='modem_location')
    parser_location.add_argument('-v', '--verbose', action='store_true', required=False)

# EFFECTS: Runs the hologram modem interfaces.
def run_hologram_modem(args):

    if args['command_selected'] not in _run_handlers:
        raise Exception('Internal CLI error: Invalid command_selected value')
    else:
        _run_handlers[args['command_selected']](args)

# EFFECTS: Converts the location encoded string into json and returns it.
def convert_location_into_json(location_obj):
    location_list = ['date', 'time', 'latitude', 'longitude', 'altitude', 'uncertainty']
    response_list = [location_obj.date, location_obj.time, location_obj.latitude,
                     location_obj.longitude, location_obj.altitude, location_obj.uncertainty]
    location_data = dict(zip(location_list, response_list))
    return json.dumps(location_data)
