#
# example-hologram-cloud-totp.py - Example of using TOTP Authentication in the Hologram Python SDK
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
    print ''
    print ''
    print 'Testing Hologram Cloud class...'
    print ''

    hologram = HologramCloud(dict(), enable_inbound=False, network='cellular', authentication_type='totp')

    result = hologram.network.connect()
    if result == False:
        print 'Failed to connect to cell network'

    recv = hologram.sendMessage('YESYESYES!',
                                topics = ['YES'],
                                timeout = 6)

    print 'RESPONSE CODE RECEIVED: ' + str(recv)
    print 'RESPONSE MESSAGE: ' + hologram.getResultString(recv)

    print ''
    print 'Testing complete.'
    print ''

    hologram.network.disconnect()
