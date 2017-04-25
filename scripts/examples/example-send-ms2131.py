#
# example-send-ms2131.py - Example of using the Huawei MS2131 modem to send messages
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

    hologram = HologramCloud(credentials, enable_inbound = False, network = 'cellular-ms2131')

    result = hologram.network.connect()
    if result == False:
        print 'Failed to connect to cell network'

    print 'Cloud type: ' + str(hologram)

    print 'Network type: ' + hologram.network_type

    recv = hologram.sendMessage("one two three!",
                                topics = ["TWO MORE TIMES","TOPIC TOPIC"],
                                timeout = 6)

    print 'DATA RECEIVED: ' + str(recv)

    print 'LOCAL IP ADDRESS: ' + hologram.network.localIPAddress
    print 'REMOTE IP ADDRESS: ' + hologram.network.remoteIPAddress
    print 'CONNECTION STATUS: ' + str(hologram.network.getConnectionStatus())

    hologram.network.disconnect()
