# Cloud.py - Hologram Python SDK Cloud interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

import logging
import Event
from Network import NetworkManager
from Authentication import *

version = '0.4.0'

class Cloud(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, credentials, send_host = '', send_port = 0,
                 receive_host = '', receive_port = 0, network = ''):

        self.credentials = credentials

        self.authenticationType = 'csrpsk'
        self.authentication = None

        # Host and port configuration
        self.send_host = send_host
        self.send_port = send_port
        self.receive_host = receive_host
        self.receive_port = receive_port

        self.event = Event.Event()

        # Logging setup.
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        logging.basicConfig(level = logging.INFO)

        # Network Configuration
        self._networkManager = NetworkManager.NetworkManager(self.event, network)

        self.message_buffer = []
        # This registers the message buffering feature based on network availability.
        self.event.subscribe('network.connected', self.clearPayloadBuffer)
        self.event.subscribe('network.disconnected', self._networkManager.networkDisconnected)

    # EFFECTS: Adds the given payload to the buffer
    def addPayloadToBuffer(self, payload):
        self.message_buffer.append(payload)

    # EFFECTS: Tells the network manager that it is connected and clears all buffered
    #          messages by sending them to the cloud.
    def clearPayloadBuffer(self):
        self._networkManager.networkConnected()
        for payload in self.message_buffer:

            recv = self.sendMessage(payload)
            self.logger.info("A buffered message has been sent since an "
                             + "active connection is established")
            self.logger.info("The buffered message sent is: " + str(payload))
            self.logger.info("The buffered response is: " + str(recv))

    @property
    def authentication(self):
        return self._authentication

    @authentication.setter
    def authentication(self, authentication):
        self._authentication = authentication

    def getSDKVersion(self):
        return version

    def sendMessage(self, messages, topics = None):
        raise NotImplementedError('Must instantiate a Cloud type')

    # EFFECTS: Sends the SMS to the destination number specified.
    def sendSMS(self, destination_number, message):
        raise NotImplementedError('Must instantiate a Cloud type')

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
        self._send_port = int(send_port)

    @property
    def receive_host(self):
        return self._receive_host

    @receive_host.setter
    def receive_host(self, receive_host):
        self._receive_host = receive_host

    @property
    def receive_port(self):
        return self._receive_port

    @receive_port.setter
    def receive_port(self, receive_port):
        self._receive_port = int(receive_port)

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event):
        self._event = event

    def getNetworkType(self):
        return repr(self._networkManager)

    @property
    def network(self):
        return self._networkManager

    @network.setter
    def network(self, network):
        self._networkManager = network

