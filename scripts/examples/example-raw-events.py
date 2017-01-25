#
# example-raw-events.py - Example of using pub/sub events in the Hologram Python SDK
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

def sayHello():
    print "Hello, it's me"

def sayHello2():
    print "Hello, it's me 2"

def wifiIsUp():
    print "WiFi is up!"

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

    hologram.message_mode.event.subscribe('message.sent', sayHello)

    print ""

    hologram.event.subscribe('message.sent', sayHello2)
    hologram.event.subscribe('wifi.connected', wifiIsUp)
    hologram.event.unsubscribe('message.sent', sayHello)

    recv = hologram.sendMessage("Hello, Python!") # Send message to Cloud

    print "DATA RECEIVED: " + recv

    print ""
    print "Testing complete."
    print ""
