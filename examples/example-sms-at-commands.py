#
# example-sms-at_commands.py - Example of using AT command socket interfaces to send
#                              SMS.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#

import sys

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
    destination_number = raw_input("What is your destination number? ")

    credentials = {'devicekey': device_key}

    hologram = HologramCloud(credentials, network='cellular', authentication_type='csrpsk')


    recv = hologram.sendSMS(destination_number, 'Hi, SMS!')

    print 'RESPONSE MESSAGE: ' + hologram.getResultString(recv)