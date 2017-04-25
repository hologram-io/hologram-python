#
# example-sms-csrpsk.py - Example of sending SMS via CSRPSK Authentication in the Hologram Python SDK
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
    hologram = HologramCloud(credentials, enable_inbound = False)

    print ''
    recv = hologram.sendSMS(destination_number, "Hello, Python!") # Send SMS to destination number
    print "RESPONSE CODE RECEIVED: " + str(recv)

    print ''
    print 'Testing complete.'
    print ''
