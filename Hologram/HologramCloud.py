# HologramCloud.py - Hologram Python SDK Cloud interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

import binascii
import json
import sys
from CustomCloud import CustomCloud
from Authentication import *
from Exceptions.HologramError import HologramError

from HologramAuth.TOTPAuthentication import TOTPAuthentication
from HologramAuth.SIMOTPAuthentication import SIMOTPAuthentication

DEFAULT_SEND_MESSAGE_TIMEOUT = 5
HOLOGRAM_HOST_SEND = 'cloudsocket.hologram.io'
HOLOGRAM_PORT_SEND = 9999
HOLOGRAM_HOST_RECEIVE= '0.0.0.0'
HOLOGRAM_PORT_RECEIVE = 4010
MAX_SMS_LENGTH = 160


# Hologram error codes
ERR_OK = 0
ERR_CONNCLOSED = 1 # Connection was closed before a terminating character
                   # but message might be fine
ERR_MSGINVALID = 2 # Couldn't parse the message
ERR_AUTHINVALID = 3 # Auth section of message was invalid
ERR_PAYLOADINVALID = 4 # Payload type was invalid
ERR_PROTINVALID = 5 # Protocol type was invalid
ERR_INTERNAL = 6 # An internal error occurred
ERR_METADATA = 7 # Metadata was formatted incorrectly
ERR_TOPICINVALID = 8 # Topic was formatted incorrectly
ERR_UNKNOWN = -1 # Unknown error

class HologramCloud(CustomCloud):

    _authentication_handlers = {
        'csrpsk' : CSRPSKAuthentication.CSRPSKAuthentication,
        'totp' : TOTPAuthentication,
        'sim-otp' : SIMOTPAuthentication,
    }

    _errorCodeDescription = {

        ERR_OK: 'Message sent successfully',
        ERR_CONNCLOSED: 'Connection was closed so we couldn\'t read the whole message',
        ERR_MSGINVALID: 'Failed to parse the message',
        ERR_AUTHINVALID: 'Auth section of the message was invalid',
        ERR_PAYLOADINVALID: 'Payload type was invalid',
        ERR_PROTINVALID: 'Protocol type was invalid',
        ERR_INTERNAL: 'Internal error in Hologram Cloud',
        ERR_METADATA: 'Metadata was formatted incorrectly',
        ERR_TOPICINVALID: 'Topic was formatted incorrectly',
        ERR_UNKNOWN: 'Unknown error'
    }

    def __init__(self, credentials, enable_inbound=False, network='',
                 authentication_type='totp'):
        super(HologramCloud, self).__init__(credentials,
                                            send_host=HOLOGRAM_HOST_SEND,
                                            send_port=HOLOGRAM_PORT_SEND,
                                            receive_host=HOLOGRAM_HOST_RECEIVE,
                                            receive_port=HOLOGRAM_PORT_RECEIVE,
                                            enable_inbound=enable_inbound,
                                            network=network)

        self.setAuthenticationType(credentials, authentication_type=authentication_type)

        if self.authenticationType == 'totp':
            self.__populate_totp_credentials()

    # EFFECTS: Authentication Configuration
    def setAuthenticationType(self, credentials, authentication_type='csrpsk'):

        if authentication_type not in HologramCloud._authentication_handlers:
            raise HologramError('Invalid authentication type: %s' % authentication_type)

        self.authenticationType = authentication_type

        self.authentication = HologramCloud._authentication_handlers[self.authenticationType](credentials)

    # EFFECTS: Sends the message to the cloud.
    def sendMessage(self, message, topics=None, timeout=DEFAULT_SEND_MESSAGE_TIMEOUT):

        if not self.is_ready_to_send():
            self.addPayloadToBuffer(message)
            return ''

        # Set the appropriate credentials required for sim otp authentication.
        if self.authenticationType == 'sim-otp':
            self.__populate_sim_otp_credentials()

        modem_type = None
        modem_id = None
        if self.network is not None:
            modem_id = self.network.modem_id
            modem_type = str(self.network.modem)

        output = self.authentication.buildPayloadString(message,
                                                        topics=topics,
                                                        modem_type=modem_type,
                                                        modem_id=modem_id,
                                                        version=self.version)

        result = super(HologramCloud, self).sendMessage(output, timeout)
        return self.__parse_result(result)

    def __parse_result(self, result):
        resultList = None
        if self.authenticationType == 'csrpsk':
            resultList = self.__parse_hologram_json_result(result)
        else:
            resultList = self.__parse_hologram_compact_result(result)

        return resultList[0]

    def __populate_totp_credentials(self):
        try:
            self.authentication.credentials['device_id'] = self.network.iccid
            self.authentication.credentials['private_key'] = self.network.imsi
        except Exception as e:
            self.logger.error('Unable to fetch device id or private key')

    def __populate_sim_otp_credentials(self):
        nonce = self.request_hex_nonce()
        command = self.authentication.generate_sim_otp_command(imsi=self.network.imsi,
                                                               iccid=self.network.iccid,
                                                               nonce=nonce)
        modem_response = self.network.get_sim_otp_response(command)
        self.authentication.generate_sim_otp_token(modem_response)

    def sendSMS(self, destination_number, message):

        self.__enforce_authentication_type_supported_for_sms()
        self.__enforce_valid_destination_number(destination_number)
        self.__enforce_max_sms_length(message)

        output = self.authentication.buildSMSPayloadString(destination_number,
                                                           message)

        self.logger.debug('Destination number: %s', destination_number)
        self.logger.debug('SMS: %s', message)

        result = super(HologramCloud, self).sendMessage(output)

        resultList = self.__parse_hologram_compact_result(result)
        return resultList[0]

    # REQUIRES: Called only when sim otp authentication is required.
    # EFFECTS: Request for a hex nonce.
    def request_hex_nonce(self):

        self.open_send_socket()

        # build nonce request payload string
        nonce_request = self.authentication.buildNonceRequestPayloadString()

        self.logger.debug("Sending nonce request with body of length %d", len(nonce_request))
        self.logger.debug('Send: %s', nonce_request)

        nonce = super(HologramCloud, self).sendMessage(message=nonce_request,
                timeout=10, close_socket=False)
        self.logger.debug('Nonce request sent.')

        resultbuf_hex = binascii.b2a_hex(nonce)

        if resultbuf_hex is None:
            raise HologramError('Internal nonce error')

        return resultbuf_hex

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


    def __parse_hologram_compact_result(self, result):

        # convert the returned response to formatted list.
        if result is None:
            return [ERR_UNKNOWN]

        resultList = []
        for x in result:
            try:
                resultList.append(int(x))
            except ValueError:
                self.logger.error('Server replied with invalid JSON [%s]', result)
                resultList = [ERR_UNKNOWN]

        if len(resultList) == 0:
            resultList = [ERR_UNKNOWN]

        return resultList

    def __enforce_max_sms_length(self, message):
        if len(message) > MAX_SMS_LENGTH:
            raise HologramError('SMS cannot be more than %d characters long' % MAX_SMS_LENGTH)

    def __enforce_valid_destination_number(self, destination_number):
        if not destination_number.startswith('+'):
            raise HologramError('SMS destination number must start with a \'+\' sign')

    def __enforce_authentication_type_supported_for_sms(self):
        if self.authenticationType is not 'csrpsk':
            raise HologramError('%s does not support SDK SMS features' % self.authenticationType)

    # REQUIRES: A result code (int).
    # EFFECTS: Returns a translated string based on the given hologram result code.
    def getResultString(self, result_code):
        if result_code not in self._errorCodeDescription:
            return 'Unknown response code'
        return self._errorCodeDescription[result_code]

    def resultWasSuccess(self, result_code):
        return result_code in (ERR_OK, ERR_CONNCLOSED)
