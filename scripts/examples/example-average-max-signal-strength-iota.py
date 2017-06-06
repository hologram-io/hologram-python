#
# example-average-max-signal-strength-iota.py - Example of getting average and max signal strength.
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

    sum_RSSI = 0.0
    sum_quality = 0.0
    num_samples = 5

    # Query for signal strength every 2 seconds...
    for i in range(num_samples):
        signal_strength = hologram.network.signal_strength
        print 'Signal strength: ' + signal_strength
        rssi, qual = signal_strength.split(',')
        sum_RSSI = sum_RSSI + int(rssi)
        sum_quality = sum_quality + int(qual)
        time.sleep(2)

    print 'Average RSSI over ' + str(num_samples) + ' samples: ' + str(sum_RSSI/num_samples)
    print 'Average quality over ' + str(num_samples) + ' samples: ' + str(sum_quality/num_samples)
