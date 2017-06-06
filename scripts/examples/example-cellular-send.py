#
# example-cellular-send.py - Example of using the iota modem to send messages
#                          to the Hologram Cloud.
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

    credentials = {'devicekey': device_key}

    hologram = HologramCloud(credentials, enable_inbound=False, network='cellular-iota')

    result = hologram.network.connect()
    if result == False:
        print 'Failed to connect to cell network'

    print 'Cloud type: ' + str(hologram)

    print 'Network type: ' + str(hologram.network_type)

    recv = hologram.sendMessage("one two three!",
                                topics = ["TOPIC 1","TOPIC 2"],
                                timeout = 3)

    print 'RESPONSE MESSAGE: ' + hologram.getResultString(recv)

    print 'LOCAL IP ADDRESS: ' + str(hologram.network.localIPAddress)
    print 'REMOTE IP ADDRESS: ' + str(hologram.network.remoteIPAddress)

    hologram.network.disconnect()
