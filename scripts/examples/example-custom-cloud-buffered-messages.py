#
# example-raw-buffered-messages.py - Example of using buffered messages in the cloud Python SDK
#
# Author: cloud <support@cloud.io>
#
# Copyright 2016 - cloud (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#

import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")

import Hologram
from Hologram.CustomCloud import CustomCloud

if __name__ == "__main__":
    print ''
    print 'Testing CustomCloud class...'
    print ''

    send_host = raw_input("What is your host? ")
    send_port = raw_input("What is your port? ")

    cloud = CustomCloud(None, send_host = send_host, send_port = send_port)

    print ''

    print 'Hologram SDK version:'
    print cloud.version

    cloud.event.broadcast('network.disconnected')

    recv = cloud.sendMessage("Hello, Python!1") # Send message to Cloud
    print "DATA RECEIVED: " + str(recv)

    recv = cloud.sendMessage("Hello, Python!2") # Send message to Cloud
    print "DATA RECEIVED: " + str(recv)

    recv = cloud.sendMessage("Hello, Python!3") # Send message to Cloud
    print "DATA RECEIVED: " + str(recv)

    cloud.event.broadcast('network.connected')

    print ''
    print 'Testing complete.'
    print ''
