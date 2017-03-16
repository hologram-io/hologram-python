# HologramCloud.py - Hologram Python SDK Cloud interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from CustomCloud import CustomCloud
from Authentication import *
import Event
import json

HOLOGRAM_HOST_SEND = 'cloudsocket.hologram.io'
HOLOGRAM_PORT_SEND = 9999
HOLOGRAM_HOST_RECEIVE= '0.0.0.0'
HOLOGRAM_PORT_RECEIVE = 4010
MAX_SMS_LENGTH = 160

# Hologram error codes
ERR_OK = 0
ERR_CONNCLOSED = 1
ERR_MSGINVALID = 2
ERR_AUTHINVALID = 3
ERR_PAYLOADINVALID = 4
ERR_PROTINVALID = 5

class HologramCloud(CustomCloud):

    _authenticationHandlers = {
        'csrpsk' : CSRPSKAuthentication.CSRPSKAuthentication,
        'totp' : TOTPAuthentication.TOTPAuthentication,
    }

    _errorCodeDescription = {

        ERR_OK: 'Message sent successfully',
        ERR_CONNCLOSED: 'Connection was closed so we couldn\'t read the whole message',
        ERR_MSGINVALID: 'Failed to parse the message',
        ERR_AUTHINVALID: 'Auth section of the message was invalid',
        ERR_PAYLOADINVALID: 'Payload type was invalid',
        ERR_PROTINVALID: 'Protocol type was invalid'
    }

    def __init__(self, credentials, enable_inbound = True, network = ''):
        super(HologramCloud, self).__init__(credentials,
                                            send_host = HOLOGRAM_HOST_SEND,
                                            send_port = HOLOGRAM_PORT_SEND,
                                            receive_host = HOLOGRAM_HOST_RECEIVE,
                                            receive_port = HOLOGRAM_PORT_RECEIVE,
                                            enable_inbound = enable_inbound,
                                            network = network)

        # Authentication Configuration
        if self.authenticationType not in HologramCloud._authenticationHandlers:
            raise Exception('Invalid authentication type: %s' % self.authenticationType)

        self.authentication = HologramCloud._authenticationHandlers[self.authenticationType](self.credentials)

    # EFFECTS: Sends the message to the cloud.
    def sendMessage(self, message, topics = None, timeout = 5):

        if not self._networkManager.networkActive:
            self.addPayloadToBuffer(message)
            return ''

        output = self.authentication.buildPayloadString(message, topics)

        result = super(HologramCloud, self).sendMessage(output, timeout)

        return self.parse_hologram_message(result)

    def sendSMS(self, destination_number, message):

        self.enforceMaxSMSLength(message)

        output = self.authentication.buildSMSPayloadString(destination_number,
                                                           message)

        result = super(HologramCloud, self).sendMessage(output)

        return self.parse_hologram_sms(result)

    # EFFECTS: Parses the hologram send response.
    def parse_hologram_message(self, result):
        try:
            return self.check_hologram_result(json.loads(result))
        except ValueError:
            self.logger.error('Invalid response from server')

        return ''

    # EFFECTS: Parses a hologram sms response.
    def parse_hologram_sms(self, result):

        # convert the returned response to formatted list.
        resultList = []
        for x in result:
            resultList.append(int(x))

        return self.check_hologram_result(resultList)

    def enforceMaxSMSLength(self, message):
        if len(message) > MAX_SMS_LENGTH:
            raise Exception('SMS cannot be more than ' + str(MAX_SMS_LENGTH)
                            + ' characters long!')

    def check_hologram_result(self, resultList):

        if not resultList:
            self.logger.error('Disconnected without getting response')
            return str(resultList)

        responseCode = int(resultList[0])

        # Check for the appropriate error response code
        if responseCode == ERR_OK:
            self.logger.info(self._errorCodeDescription[responseCode])
        else:
            self.logger.error('Unable to receive message')

            # Look up the hologram error code description and see if error can
            # be identified.
            try:
                description = self._errorCodeDescription[responseCode]
                if description is not None:
                    self.logger.error(description)
            except KeyError:
                self.logger.error('Unknown error: ' + str(resultList))

        return str(responseCode)
