#
# example-custom-receive-with-message-received.py - Example of using message.received
# event handler in the Hologram Python SDK
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

from Hologram.CustomCloud import CustomCloud

def sayMessageReceived():
    print 'A message has been received!'

if __name__ == "__main__":
    print ""
    print ""
    print "Testing Hologram Cloud class..."
    print ""
    print "* Note: You can obtain CSRPSK IDs and Keys from the Devices page"
    print "* at https://dashboard.hologram.io"
    print ""

    receive_host = raw_input("What is your host? ")
    receive_port = raw_input("What is your port? ")

    customCloud = CustomCloud(None, receive_host=receive_host,
                              receive_port=receive_port,
                              enable_inbound = True)

    customCloud.event.subscribe('message.received', sayMessageReceived)

    # send your messages here.
    print 'sleeping for 20 seconds'
    print 'Send your messages now!'
    time.sleep(20)
    print "woke up..."

    customCloud.closeReceiveSocket()
    customCloud.openReceiveSocket()

    print 'sleeping for another 20 seconds'
    print 'Send your messages now!'
    time.sleep(20)
    print "woke up..."

    customCloud.closeReceiveSocket()

    recv = customCloud.popReceivedMessage()
    print "DATA RECEIVED: " + str(recv)

    print ""
    print "Testing complete."
    print ""
