#
# example-cellular-send.py - Example of using a supported modem to send messages
#                            to the Hologram Cloud.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
import logging
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

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    hologram = HologramCloud(dict(), authentication_type='sim-otp',
                             network='cellular')

    result = hologram.network.connect()
    if result == False:
        print 'Failed to connect to cell network'

    recv = hologram.sendMessage("one two three!",
                                topics = ["TOPIC1","TOPIC2"],
                                timeout = 3)

    print 'RESPONSE MESSAGE: ' + hologram.getResultString(recv)

    hologram.network.disconnect()
