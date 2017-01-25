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

from Hologram import Hologram
from Hologram.Credentials import Credentials

if __name__ == "__main__":
    print ""
    print ""
    print "Testing Hologram Cloud class..."
    print ""
    print "* Note: You can obtain CSRPSK IDs and Keys from the Devices page"
    print "* at https://dashboard.hologram.io"
    print ""

    CSRPSKID = raw_input("What is your CSRPSK ID? ")
    CSRPSKKey = raw_input("What is your CSRPSK Key? ")
    destination_number = raw_input("What is your destination number? ")

    credentials = Credentials(CSRPSKID, CSRPSKKey)

    hologram = Hologram(credentials)

    print ""
    recv =hologram.sendSMS(destination_number, "Hello, Python!") # Send SMS to destination number
    print "DATA RECEIVED: " + str(recv)

    print ""
    print "Testing complete."
    print ""
