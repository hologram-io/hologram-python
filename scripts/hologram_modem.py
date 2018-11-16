#!/usr/bin/env python

# hologram_modem.py - Hologram Python SDK command line interface (CLI) for modem interfaces.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License

from Hologram.CustomCloud import CustomCloud
from Exceptions.HologramError import HologramError
from hologram_util import handle_timeout
from hologram_util import VAction
import json
import psutil
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

help_reset = '''This subcommand causes the modem to restart itself.\n
'''

help_radio_off = '''This subcommand causes the modem to turn off the cellular
radio\n
'''

help_radio_on = '''This subcommand causes the modem to turn on the cellular
radio\n
'''

def run_modem_connect(args):
    print 'Note: "hologram modem connect" is deprecated '\
            'in favor of "hologram network connect"'
    cloud = CustomCloud(None, network='cellular')
    cloud.network.disable_at_sockets_mode()
    res = cloud.network.connect()
    if res:
        print 'PPP session started'
    else:
        print 'Failed to start PPP'

def run_modem_disconnect(args):
    print 'Note: "hologram modem disconnect" is deprecated '\
            'in favor of "hologram network disconnect"'
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

def run_modem_signal(args):
    cloud = CustomCloud(None, network='cellular')

    if args['repeat'] != 0:
        while True:
            print 'Signal strength: ' + cloud.network.signal_strength
            handle_timeout(args['repeat'])
    else:
        print 'Signal strength: ' + str(cloud.network.signal_strength)

def run_modem_reset(args):
    cloud = CustomCloud(None, network='cellular')
    cloud.network.modem.reset()
    print 'Restarted modem'

def run_modem_radio_off(args):
    cloud = CustomCloud(None, network='cellular')
    res = cloud.network.modem.radio_power(False)
    if res:
        print 'Modem radio disabled'
    else:
        print 'Failure to disable radio'

def run_modem_radio_on(args):
    cloud = CustomCloud(None, network='cellular')
    res = cloud.network.modem.radio_power(True)
    if res:
        print 'Modem radio enabled'
    else:
        print 'Failure to enable radio'


def run_modem_sim(args):
    cloud = CustomCloud(None, network='cellular')
    print 'ICCID: ' + str(cloud.network.iccid)

def run_modem_operator(args):
    cloud = CustomCloud(None, network='cellular')
    print 'Operator: ' + str(cloud.network.operator)

def run_modem_type(args):
    cloud = CustomCloud(None, network='cellular')
    print 'Type: %s' % cloud.network.description

def run_modem_location(args):
    cloud = CustomCloud(None, network='cellular')
    location_obj = cloud.network.location
    if location_obj is None:
        print 'Location: Not Available'
    else:
        print 'Location: ' + convert_location_into_json(location_obj)

_run_handlers = {
    'modem_connect': run_modem_connect,
    'modem_disconnect': run_modem_disconnect,
    'modem_sim': run_modem_sim,
    'modem_operator': run_modem_operator,
    'modem_signal': run_modem_signal,
    'modem_type': run_modem_type,
    'modem_location': run_modem_location,
    'modem_reset': run_modem_reset,
    'modem_radio_on': run_modem_radio_on,
    'modem_radio_off': run_modem_radio_off
}

# EFFECTS: Parses the CLI arguments as options to the hologram modem subcommand.
def parse_hologram_modem_args(parser):
    # Create a subparser
    subparsers = parser.add_subparsers(title='subcommands')

    # Connect
    parser_connect = subparsers.add_parser('connect', help=help_connect)
    parser_connect.set_defaults(command_selected='modem_connect')
    parser_connect.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # Disconnect
    parser_disconnect = subparsers.add_parser('disconnect', help=help_disconnect)
    parser_disconnect.set_defaults(command_selected='modem_disconnect')
    parser_disconnect.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # Signal
    parser_signal = subparsers.add_parser('signal', help=help_signal)
    parser_signal.set_defaults(command_selected='modem_signal')
    parser_signal.add_argument('--repeat', type=int, default=0, nargs='?',
                               help='Time period for each signal read')
    parser_signal.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # Operator
    parser_operator = subparsers.add_parser('operator', help=help_operator)
    parser_operator.set_defaults(command_selected='modem_operator')
    parser_operator.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # SIM
    parser_sim = subparsers.add_parser('sim', help=help_sim)
    parser_sim.set_defaults(command_selected='modem_sim')
    parser_sim.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # Type
    parser_type = subparsers.add_parser('type', help=help_type)
    parser_type.set_defaults(command_selected='modem_type')
    parser_type.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # Location
    parser_location = subparsers.add_parser('location', help=help_location)
    parser_location.set_defaults(command_selected='modem_location')
    parser_location.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # Reset
    parser_reset = subparsers.add_parser('reset', help=help_reset)
    parser_reset.set_defaults(command_selected='modem_reset')
    parser_reset.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # radio-on
    parser_radio_on = subparsers.add_parser('radio-on', help=help_reset)
    parser_radio_on.set_defaults(command_selected='modem_radio_on')
    parser_radio_on.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)

    # radio-off
    parser_radio_off = subparsers.add_parser('radio-off', help=help_reset)
    parser_radio_off.set_defaults(command_selected='modem_radio_off')
    parser_radio_off.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)


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
