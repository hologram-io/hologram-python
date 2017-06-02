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
from scripts.hologram_receive import parse_hologram_receive_args

def parse_hologram_spacebridge_args(parser):
    parse_hologram_receive_args(parser)
    parser.set_defaults(command_selected='spacebridge')

def run_hologram_spacebridge(args):
    args['command_selected'] = 'receive_data'
    run_hologram_receive(args)
