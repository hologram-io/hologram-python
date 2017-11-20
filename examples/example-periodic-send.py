#
# example-hologram-cloud-periodic-send.py - Example for sending periodic messages
#                                           to the Hologram cloud.
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#

import sys
import time

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")

from Hologram.HologramCloud import HologramCloud

if __name__ == "__main__":
    print ""
    print ""
    print "Testing Hologram Cloud class..."
    print ""
    print "* Note: You can obtain device keys from the Devices page"
    print "* at https://dashboard.hologram.io"
    print ""

    device_key = raw_input("What is your device key? ")

    credentials = {'devicekey': device_key}

    hologram = HologramCloud(credentials, authentication_type='csrpsk')

    print 'Sending a periodic message every 30 seconds...'
    recv = hologram.sendPeriodicMessage(30, 'This is a periodic message',
                                        topics=['PERIODICMESSAGES'],
                                        timeout=6)

    print 'sleeping for 40 seconds...'
    time.sleep(40)
    print 'waking up!'

    hologram.stopPeriodicMessage()

    print ''
    print 'Testing complete.'
    print ''
