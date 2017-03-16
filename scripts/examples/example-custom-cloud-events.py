#
# example-custom-cloud-events.py - Example of using pub/sub events in the Hologram Python SDK
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

from Hologram.CustomCloud import CustomCloud

def sayHello():
    print "Hello, it's me"

def sayHello2():
    print "Hello, it's me 2"

def wifiIsUp():
    print "WiFi is up!"

if __name__ == "__main__":
    print ''
    print 'Testing Custom Cloud class...'
    print ''

    send_host = raw_input("What is your host? ")
    send_port = raw_input("What is your port? ")

    customCloud = CustomCloud(None, send_host=send_host, send_port=send_port)

    customCloud.event.subscribe('message.sent', sayHello)

    print ""

    customCloud.event.subscribe('message.sent', sayHello2)
    customCloud.event.subscribe('wifi.connected', wifiIsUp)
    customCloud.event.unsubscribe('message.sent', sayHello)

    recv = customCloud.sendMessage("Hello, Python!") # Send message to Cloud

    print "DATA RECEIVED: " + str(recv)

    print ''
    print 'Testing complete.'
    print ''
