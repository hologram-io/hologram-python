#
# example-serial-interface.py - Example of using serial interface with a supported modem.
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

if __name__ == '__main__':

    hologram = HologramCloud(None, enable_inbound=False, network='cellular-iota')

    print 'Signal strength: ' + hologram.network.signal_strength
    print 'IMSI: ' + hologram.network.imsi
    print 'ICCID: ' + hologram.network.iccid
    print 'Operator: ' + hologram.network.operator
    print 'Modem name: ' + hologram.network.active_modem_interface

    location = hologram.network.location
    print 'Latitude: ' + location.latitude
    print 'Longitude: ' + location.longitude
    print 'Date: ' + location.date
