#
# example-receive-sms.py - Example of receiving SMS on a supported modem.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#

import sys
import time
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

    hologram = HologramCloud(None, enable_inbound=False, network='cellular-iota')

    hologram.enableSMS()

    print 'waiting for 20 seconds...'
    time.sleep(20)

    hologram.disableSMS()

    sms_obj = hologram.popReceivedSMS()

    if sms_obj is None:
        print 'sms_obj: ' + str(sms_obj)
    else:
        print 'sender: ' + str(sms_obj.sender)
        print sms_obj.timestamp
        print 'message: ' + str(sms_obj.message)
