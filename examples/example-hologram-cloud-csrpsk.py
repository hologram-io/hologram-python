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
    print "* Note: You can obtain device keys from the Devices page"
    print "* at https://dashboard.hologram.io"
    print ""

    device_key = raw_input("What is your device key? ")

    credentials = {'devicekey': device_key}

    hologram = HologramCloud(credentials, enable_inbound = False)

    print 'Hologram SDK version:'
    print hologram.version

    print ''
    print 'Cloud type: ' + str(hologram)
    print ''
    print 'Network type: ' + hologram.network_type
    print ''

    recv = hologram.sendMessage("one two three!",
                                topics = ["TWO MORE TIMES","TOPIC TOPIC"],
                                timeout = 6)

    print 'RESPONSE CODE RECEIVED: ' + str(recv)
    print 'RESPONSE MESSAGE: ' + hologram.getResultString(recv)

    print ''
    print 'Testing complete.'
    print ''
