#!/usr/bin/env python

# hologram_activate.py - Hologram Python SDK command line interface (CLI) for activating
#                        devices.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

import copy
import getpass
import sys
import time

from Hologram.HologramCloud import HologramCloud
from Hologram.Api import Api
from Exceptions.HologramError import HologramError
from hologram_util import VAction

CHECK_LIVE_SIM_STATE_MAX_TIMEOUT = 120 # 2 mins for max timeout
CHECK_LIVE_SIM_STATE_INTERVAL = 5

# EFFECTS: Parses hologram activate CLI options.
def parse_hologram_activate_args(parser):
    parser.set_defaults(command_selected='activate')
    parser.add_argument('-v', nargs='?', action=VAction, dest='verbose', required=False)
    parser.add_argument('--apikey', nargs='?', help='Hologram organization API key')

# EFFECTS: Handles all hologram_send operations.
#          This function will call the appropriate cloud/sms handler.
def run_hologram_activate(args):

    hologram = HologramCloud(dict(), network='cellular')
    sim = hologram.network.iccid

    if sim is None:
        raise HologramError('Failed to fetch SIM number from the modem')

    func_args = dict()

    if args['apikey'] is None:
        (username, password) = prompt_for_username_and_password()
        func_args['username'] = username
        func_args['password'] = password
    else:
        func_args['apikey'] = args['apikey']

    api = Api(**func_args)

    success, plans = api.getPlans()

    if success == False:
        raise HologramError('Failed to fetch plans')

    planIdToZonesDict = populate_valid_plans(plans)

    selected_plan, plan_name = prompt_for_plan(plans, planIdToZonesDict)
    selected_zone = prompt_for_zone(planIdToZonesDict[selected_plan])

    # preview
    success, response = api.activateSIM(sim=sim, plan=selected_plan,
                                        zone=selected_zone, preview=True)

    if success == False:
        print('Activation verification failed: %s' % response)
        return
    elif not confirm_activation(sim, plan_name, selected_plan, selected_zone, response['total_cost']):
        return


    success, response = api.activateSIM(sim=sim, plan=selected_plan,
                                        zone=selected_zone)

    if success == True:
        print('Activating SIM... (this may take up to a few minutes)')
    else:
        print('Activation failed')
        return

    start_time = time.time()
    while time.time() < start_time + CHECK_LIVE_SIM_STATE_MAX_TIMEOUT:
        success, sim_state = api.getSIMState(sim)

        if sim_state == 'LIVE':
            break

        time.sleep(CHECK_LIVE_SIM_STATE_INTERVAL)

    if sim_state == 'LIVE':
        print('Activation successful!')
    else:
        print('SIM is still not activated. Check status in a few minutes on Hologram Dashboard (https://dashboard.hologram.io/) or contact support@hologram.io with any further delays')


def confirm_activation(sim, plan_name, selected_plan, selected_zone, total_cost):
    response = raw_input("Activate SIM #%s on %s Zone %s for $%.2f (y/N)? " % (sim, plan_name, str(selected_zone), total_cost))
    return response == 'y'

# EFFECTS: Populate valid and available plans and returns a plan -> zones dictionary.
def populate_valid_plans(plans):
    planIdToZonesDict = dict()

    for plan in plans:
        if is_available_developer_plan(plan) or is_pay_as_you_go_plan(plan):
            planIdToZonesDict[plan['id']] = copy.deepcopy(plan['tiers']['BASE']['zones'])
    return planIdToZonesDict

def prompt_for_plan(plans, planIdToZonesDict):
    planIdToNames = dict()

    print('Available plans: ')

    if not plans:
        print('  [NONE]')
        return None

    # Print plan options
    for plan in plans:
        if plan['id'] in planIdToZonesDict:
            planIdToNames[plan['id']] = plan['name']
            print_plan_description(plan)

    while True:
        try:
            planid = raw_input('Choose the plan id for this device: ')
            if not planid.isdigit():
                print('Error: Invalid plan id')
                continue
            planid = int(planid)
            if planid not in planIdToZonesDict:
                print('Error: Invalid plan id')
                continue
            return planid, planIdToNames[planid]
        except KeyboardInterrupt as e:
            sys.exit(1)
    return None, None

# REQUIRES: A zones dictionary.
# EFFECTS: Prompts the user for a zoneid based on all available zones.
#          Returns that zoneid.
def prompt_for_zone(zones):

    zoneid = None
    zoneids = []

    for zoneid, zone_details in zones.iteritems():
        zoneids.append(zoneid)
        print_zone_description(zoneid, zone_details)

    # There's only one available zone, so we can just select that without asking
    # the user.
    if len(zoneids) == 1:
        return zoneids[0]

    while True:
        try:
            zone = raw_input('Choose the zone for this device: ')
            if zone not in zoneids:
                print('Error: Invalid zone')
                continue
            return zone
        except KeyboardInterrupt as e:
            sys.exit(1)
    return None

# EFFECTS: Returns true if the given plan is a developer plan with the
#          available flag set to True.
def is_available_developer_plan(plan):
    return 'available' in plan and plan['available'] == True

# EFFECTS: Returns true if it's a pay as you go plan, false otherwise.
def is_pay_as_you_go_plan(plan):
    return plan['data'] == 0

# REQUIRES: The plan object to be formatted properly.
# EFFECTS: Prints the plan description.
def print_plan_description(plan):
    print("-----------------------------------------")
    print("  Plan ID #  : %d" % plan['id'])
    print("  Name       : %s" % plan['name'])
    print("-----------------------------------------")

# REQUIRES: The zone object to be formatted properly.
# EFFECTS: Prints the zone description.
def print_zone_description(zoneid, zone_details):
    print("-----------------------------------------")
    print("  ZONE                : %s" % str(zoneid))
    print("  Data ($/MB)         : $%s" % str(zone_details['overage']))
    print("  Monthly Platform Fee: $%s" % str(zone_details['amount']))
    print("-----------------------------------------")

# EFFECTS: Prompts user for username and password, returns them as a tuple.
def prompt_for_username_and_password():

    try:
        username = raw_input("Please enter your Hologram username: ")
        password = getpass.getpass("Please enter your Hologram password: ")
    except KeyboardInterrupt as e:
        sys.exit(1)

    return (username, password)
