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

    hologram = HologramCloud(None, network='cellular')

    print 'Signal strength: ' + str(hologram.network.signal_strength)
    print 'Modem id: ' + str(hologram.network.modem_id)
    print 'IMSI: ' + str(hologram.network.imsi)
    print 'ICCID: ' + str(hologram.network.iccid)
    print 'Operator: ' + str(hologram.network.operator)
    print 'Modem name: ' + str(hologram.network.active_modem_interface)

    location = hologram.network.location
    if location is None:
        print 'Location: ' + str(location)
    else:
        print 'Latitude: ' + str(location.latitude)
        print 'Longitude: ' + str(location.longitude)
        print 'Date: ' + str(location.date)
