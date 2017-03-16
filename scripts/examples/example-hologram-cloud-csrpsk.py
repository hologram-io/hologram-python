#
# example-cloud-csrpsk.py - Example of using CSRPRSK Authentication in the Hologram Python SDK
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
    print "* Note: You can obtain cloud IDs and keys from the Devices page"
    print "* at https://dashboard.hologram.io"
    print ""

    cloudID = raw_input("What is your cloud ID? ")
    cloudKey = raw_input("What is your cloud key? ")

    credentials = {'cloud_id': cloudID, 'cloud_key': cloudKey}

    hologram = HologramCloud(credentials, enable_inbound = False)

    print ''
    print 'Available network interfaces:'
    print hologram.network.listAvailableInterfaces()

    print ''
    print 'Cloud type: ' + str(hologram)
    print ''
    print 'Network type: ' + hologram.getNetworkType()
    print ''

    recv = hologram.sendMessage("one two three!",
                                topics = ["TWO MORE TIMES","TOPIC TOPIC"],
                                timeout = 6)

    print 'DATA RECEIVED: ' + str(recv)

    print ''
    print 'Testing complete.'
    print ''
