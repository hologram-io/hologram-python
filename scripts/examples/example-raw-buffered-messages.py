#
# example-raw-buffered-messages.py - Example of using buffered messages in the Hologram Python SDK
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

import Hologram
from Hologram.Hologram import Hologram
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

    print "Hologram SDK version:"
    print hologram.getSDKVersion()

    hologram.event.broadcast('network.disconnected')

    recv = hologram.sendMessage("Hello, Python!1") # Send message to Cloud
    print "DATA RECEIVED: " + str(recv)

    recv = hologram.sendMessage("Hello, Python!2") # Send message to Cloud
    print "DATA RECEIVED: " + str(recv)

    recv = hologram.sendMessage("Hello, Python!3") # Send message to Cloud
    print "DATA RECEIVED: " + str(recv)

    hologram.event.broadcast('network.connected')

    print ""
    print "Testing complete."
    print ""
