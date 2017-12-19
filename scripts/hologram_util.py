# hologram_util.py - Hologram Python SDK command line interface (CLI) util
#                    helper methods
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License

import argparse
import time
import sys

DEFAULT_DELAY_INTERVAL = 0

def handle_timeout(timeout):

    try:
        if timeout != -1:
            print 'waiting for ' + str(timeout) + ' seconds...'
            time.sleep(timeout)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt as e:
        sys.exit(e)

def handle_polling(timeout, fx, delay_interval=DEFAULT_DELAY_INTERVAL):
    if timeout != -1:
        print 'waiting for ' + str(timeout) + ' seconds...'
        end = time.time() + timeout
        while time.time() < end:
            fx()
            time.sleep(delay_interval)
    else:
        while True:
            fx()
            time.sleep(delay_interval)

class VAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        # print 'values: {v!r}'.format(v=values)
        if values==None:
            values='1'
        try:
            values=int(values)
        except ValueError:
            values=values.count('v')+1
        setattr(args, self.dest, values)
