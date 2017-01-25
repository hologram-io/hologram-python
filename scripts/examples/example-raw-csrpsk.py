#
# example-raw-csrpsk.py - Example of using CSRPSK Authentication in the Hologram Python SDK
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

    credentials = Credentials(CSRPSKID, CSRPSKKey)

    hologram = Hologram(credentials, message_mode='tcp-other')

    hologram.send_host = 'cloudsocket.hologram.io'
    hologram.send_port = 9999

    print ""
    recv = hologram.sendMessage("Hello, Python!") # Send message to Cloud

    print "DATA RECEIVED: " + str(recv)

    print ""
    print "Testing complete."
    print ""
