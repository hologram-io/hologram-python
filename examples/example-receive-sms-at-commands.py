#
# example-sms-at_commands.py - Example of using AT command socket interfaces to send
#                              SMS.
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

def popReceivedMessage():
    recv = hologram.popReceivedMessage()
    if recv is not None:
        print 'Received message: ' + str(recv)

def handle_polling(timeout, fx, delay_interval=0):
    try:
        if timeout != -1:
            print 'waiting for ' + str(timeout) + ' seconds...'
            end = time.time() + timeout
            while time.time() < end:
                fx()
                time.sleep(delay_interval)
        else:
            while True:
                fx()
                time.sleep(delay_interval)
    except KeyboardInterrupt as e:
        sys.exit(e)

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

    hologram = HologramCloud(credentials, network='cellular', authentication_type='csrpsk')

    hologram.openReceiveSocket()
    print ('Ready to receive data...')

    handle_polling(40, popReceivedMessage, 1)

    hologram.closeReceiveSocket()