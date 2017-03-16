#
# example-custom-cloud-basic.py - Example of using a CustomCloud in the Hologram Python SDK
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

if __name__ == "__main__":
    print ""
    print "Testing Cloud class..."
    print ""

    send_host = raw_input("What is your host? ")
    send_port = raw_input("What is your port? ")

    customCloud = CustomCloud(None, send_host = send_host, send_port = send_port)

    print ''
    recv = customCloud.sendMessage('Hello, Python!') # Send message to Cloud

    print 'DATA RECEIVED: ' + str(recv)

    print ''
    print 'Testing complete.'
    print ''
