#
# example-cloud-buffered-messages.py - Example of using buffered messages in the Hologram Python SDK
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
    print ''
    print ''
    print "Testing Hologram Cloud class..."
    print ''
    print "* Note: You can obtain device keys from the Devices page"
    print "* at https://dashboard.hologram.io"
    print ''

    device_key = raw_input('What is your device key? ')

    credentials = {'devicekey': device_key}

    hologram = HologramCloud(credentials, enable_inbound = False)
    print ''

    hologram.event.broadcast('network.disconnected')

    recv = hologram.sendMessage("one!", topics = ["TWO MORE TIMES","TOPIC TOPIC"]) # Send advanced message
    print "RESPONSE CODE RECEIVED: " + str(recv)

    recv = hologram.sendMessage("two!", topics = ["TWO MORE TIMES","TOPIC TOPIC"]) # Send advanced message
    print "RESPONSE CODE RECEIVED: " + str(recv)

    recv = hologram.sendMessage("three!", topics = ["TWO MORE TIMES","TOPIC TOPIC"]) # Send advanced message
    print "RESPONSE CODE RECEIVED: " + str(recv)

    hologram.event.broadcast('network.connected')

    print ''
    print 'Testing complete.'
    print ''
