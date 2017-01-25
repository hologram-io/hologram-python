# hologram_send.py - Hologram Python SDK command line interface (CLI) for sending messages to the cloud
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import argparse
import sys
import hjson

sys.path.append(".")
sys.path.append("..")

import Hologram
from Hologram.Hologram import Hologram
from Hologram.Credentials import Credentials

script_description = '''
This hologram_send program sends a message (string) to the cloud
'''

def parseArguments():

    parser = argparse.ArgumentParser(description=script_description)

    parser.add_argument("message", nargs = '?',
                        help = 'message that will be sent to the cloud')

    parser.add_argument('--cloud_id', nargs = '?',
                        help = 'Hologram cloud ID (4 characters long)')

    parser.add_argument('--cloud_key', nargs = '?',
                        help = 'Hologram cloud Key (4 characters long)')

    parser.add_argument('--host', nargs = '?', help = argparse.SUPPRESS)

    parser.add_argument('-p', '--port', type = int, nargs = '?',
                        help = argparse.SUPPRESS)

    parser.add_argument('-t', '--topic', nargs = '*',
                        help = 'Topics for the message (optional)')

    parser.add_argument('-f', '--file', nargs = '?',
                        help = 'Configuration (HJSON) file that stores the required credentials to send the message to the cloud')

    return parser.parse_args()

def main():

    args = parseArguments()

    if args.file:
        data = None
        with open(args.file) as credentials_file:
            data = hjson.load(credentials_file)

        if not args.cloud_id:
            args.cloud_id = data['cloud_id']

        if not args.cloud_key:
            args.cloud_key = data['cloud_key']

    credentials = Credentials(args.cloud_id, args.cloud_key)

    # Setting the credentials host and port.
    if args.host:
        credentials.host = args.host
    else:
        credentials.host = 'cloudsocket.hologram.io'

    if args.port:
        credentials.port = args.port
    else:
        credentials.port = 9999

    if args.topic:
        hologram = Hologram(credentials)
        recv = hologram.sendMessage(args.message, topics = args.topic)
        print "DATA RECEIVED: " + str(recv)
    else:
        hologram = Hologram(credentials, message_mode='tcp-other')
        hologram.send_host = credentials.send_host
        hologram.send_port = credentials.send_port
        recv = hologram.sendMessage(args.message)
        print "DATA RECEIVED: " + str(recv)

if __name__ == "__main__": main()
