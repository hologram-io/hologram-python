# HologramCloud.py - Hologram Python SDK Cloud interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

import json
import sys
from CustomCloud import CustomCloud
from Authentication import *
from Exceptions.HologramError import HologramError
import Event

from HologramAuth.TOTPAuthentication import TOTPAuthentication

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
ERR_INTERNAL = 6
ERR_UNKNOWN = -1


class HologramCloud(CustomCloud):

    _authentication_handlers = {
        'csrpsk' : CSRPSKAuthentication.CSRPSKAuthentication,
        'totp' : TOTPAuthentication,
    }

    _errorCodeDescription = {

        ERR_OK: 'Message sent successfully',
        ERR_CONNCLOSED: 'Connection was closed so we couldn\'t read the whole message',
        ERR_MSGINVALID: 'Failed to parse the message',
        ERR_AUTHINVALID: 'Auth section of the message was invalid',
        ERR_PAYLOADINVALID: 'Payload type was invalid',
        ERR_PROTINVALID: 'Protocol type was invalid',
        ERR_INTERNAL: 'Internal error in Hologram Cloud',
        ERR_UNKNOWN: 'Unknown error'
    }

    def __init__(self, credentials, enable_inbound = True, network = '',
                 authentication_type = 'csrpsk'):
        super(HologramCloud, self).__init__(credentials,
                                            send_host=HOLOGRAM_HOST_SEND,
                                            send_port=HOLOGRAM_PORT_SEND,
                                            receive_host=HOLOGRAM_HOST_RECEIVE,
                                            receive_port=HOLOGRAM_PORT_RECEIVE,
                                            enable_inbound=enable_inbound,
                                            network=network)

        self.setAuthenticationType(credentials, authentication_type=authentication_type)

    # EFFECTS: Authentication Configuration
    def setAuthenticationType(self, credentials, authentication_type='csrpsk'):

        try:
            if authentication_type not in HologramCloud._authentication_handlers:
                raise HologramError('Invalid authentication type: %s' % authentication_type)

            self.authenticationType = authentication_type

            self.authentication = HologramCloud._authentication_handlers[self.authenticationType](credentials)
        except HologramError as e:
            self.logger.error(repr(e))
            sys.exit(1)

    # EFFECTS: Sends the message to the cloud.

    def sendMessage(self, message, topics = None, timeout = 5):

        if not self._networkManager.networkActive:
            self.addPayloadToBuffer(message)
            return ''

        output = self.authentication.buildPayloadString(message, topics)

        result = super(HologramCloud, self).sendMessage(output, timeout)

        resultList = None
        if self.authenticationType == 'csrpsk':
            resultList = self.__parse_hologram_json_result(result)
        else:
            resultList = self.__parse_hologram_compact_result(result)

        return resultList[0]

    def sendSMS(self, destination_number, message):

        try:
            self.__enforce_max_sms_length(message)
        except HologramError as e:
            self.logger.error(repr(e))
            sys.exit(1)

        output = self.authentication.buildSMSPayloadString(destination_number,
                                                           message)

        self.logger.debug('Destination number: %s', destination_number)
        self.logger.debug('SMS: %s', message)

        result = super(HologramCloud, self).sendMessage(output)

        resultList = self.__parse_hologram_compact_result(result)
        return resultList[0]

    def enableSMS(self):
        return self.network.enableSMS()

    def disableSMS(self):
        return self.network.disableSMS()

    def popReceivedSMS(self):
        return self.network.popReceivedSMS()

    # EFFECTS: Parses the hologram send response.
    def __parse_hologram_json_result(self, result):
        try:
            resultList = json.loads(result)
            resultList[0] = int(resultList[0])
        except ValueError:
            self.logger.error('Server replied with invalid JSON [%s]', result)
            resultList = [ERR_UNKNOWN]
        return resultList


    # EFFECTS: Parses a hologram sms response.
    def __parse_hologram_compact_result(self, result):

        # convert the returned response to formatted list.
        resultList = []
        if not result:
            resultList = [ERR_UNKNOWN]
        for x in result:
            try:
                resultList.append(int(x))
            except ValueError:
                self.logger.error('Server replied with invalid JSON [%s]', result)
                resultList = [ERR_UNKNOWN]
        return resultList

    def __enforce_max_sms_length(self, message):
        if len(message) > MAX_SMS_LENGTH:
            raise HologramError('SMS cannot be more than %d characters long' % MAX_SMS_LENGTH)

    # REQUIRES: A result code (int).
    # EFFECTS: Returns a translated string based on the given hologram result code.
    def getResultString(self, resultCode):
        if resultCode not in self._errorCodeDescription:
            return 'Unknown response code'
        return self._errorCodeDescription[resultCode]
