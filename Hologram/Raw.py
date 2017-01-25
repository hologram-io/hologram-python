# Raw.py - Hologram Python SDK Raw interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

import socket
import logging
import sys
import Event

class Raw(object):

    def __init__(self, authentication, send_host = '', send_port = '', debug = False):
        self.authentication = authentication
        self.event = Event.Event()
        self.debug = debug
        self.send_host = send_host
        self.send_port = send_port
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.networkDisconnected = True
        logging.basicConfig(level=logging.INFO)
        self.message_buffer = []
        self.event.subscribe('network.connected', self.clearPayloadBuffer)
        self.event.subscribe('network.disconnected', self.disconnectNetwork)

    # EFFECTS: Sends the message to the cloud.
    def sendMessage(self, message, timeout = 5):

        try:
            if self.networkDisconnected:
                self.addPayloadToBuffer(message)
                return ""

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((self._send_host, self._send_port))

            self.logger.info("Connecting to %s:", self._send_host)
            self.logger.info("%s", self._send_port)

            self.logger.info("Sending message of length %d...", len(message))
            self.logger.info("Send: ")

            self.logger.info(message)

            sock.send(message)

            self.logger.info('Sent.')

            resultbuf = ''
            while True:
                try:
                    result = sock.recv(1024)
                except socket.timeout:
                    break
                if not result:
                    break
                resultbuf += result

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

            self.event.broadcast('message.sent')
            return resultbuf

        except (IOError):
            self.logger.info("An error occurred while attempting to send the "
                             + "message to the cloud")
            self.logger.info("Please try again.")
            return ""

    def sendSMS(self, destination_number, message):
        raise NotImplementedError('Cannot send SMS via custom Cloud')

    # EFFECTS: Adds the given payload to the buffer
    def addPayloadToBuffer(self, payload):
        self.message_buffer.append(payload)

    # EFFECTS: Sets networkDisconnected to false and clears all buffered
    #          messages by sending them to the cloud.
    def clearPayloadBuffer(self):
        self.networkDisconnected = False
        for payload in self.message_buffer:
            recv = self.sendMessage(payload)
            self.logger.info("A buffered message has been sent since an "
                             + "active connection is established")
            self.logger.info("The buffered message sent is: " + str(payload))
            self.logger.info("The buffered response is: " + str(recv))

    # EFFECTS: Event handler function that sets the network disconnect flag.
    def disconnectNetwork(self):
        self.networkDisconnected = True

    @property
    def send_host(self):
        return self._send_host

    @send_host.setter
    def send_host(self, send_host):
        self._send_host = send_host

    @property
    def send_port(self):
        return self._send_port

    @send_port.setter
    def send_port(self, send_port):
        self._send_port = send_port
