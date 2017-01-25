# HologramCloud.py - Hologram Python SDK Cloud interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from Raw import Raw
import Event

HOLOGRAM_HOST = "cloudsocket.hologram.io"
HOLOGRAM_PORT = 9999
MAX_SMS_LENGTH = 160

# Hologram error codes
ERR_OK = 0
ERR_CONNCLOSED = 1
ERR_MSGINVALID = 2
ERR_AUTHINVALID = 3
ERR_PAYLOADINVALID = 4
ERR_PROTINVALID = 5

errorCodeDescription = {

    ERR_OK: 'message sent successfully',
    ERR_CONNCLOSED: 'connection was closed so we couldn\'t read the whole message',
    ERR_MSGINVALID: 'Failed to parse the message',
    ERR_AUTHINVALID: 'Auth section of the message was invalid',
    ERR_PAYLOADINVALID: 'Payload type was invalid',
    ERR_PROTINVALID: 'Protocol type was invalid'
}

class HologramCloud(Raw):

    def __init__(self, authentication, debug = False):
        super(HologramCloud, self).__init__(authentication = authentication,
                                            send_host = HOLOGRAM_HOST,
                                            send_port = HOLOGRAM_PORT,
                                            debug = debug)
        self.event = Event.Event()

    # EFFECTS: Sends the message to the cloud.
    def sendMessage(self, message, topics = None, timeout = 5):

        if self.networkDisconnected:
            self.addPayloadToBuffer(message)
            return ""

        output = self.authentication.buildPayloadString(message, topics)

        result = super(HologramCloud, self).sendMessage(output, timeout)

        return self.parse_hologram_result(result)

    def sendSMS(self, destination_number, message):

        self.enforceMaxSMSLength(message)

        output = self.authentication.buildSMSPayloadString(destination_number,
                                                           message)

        result = super(HologramCloud, self).sendMessage(output)

        return self.parse_hologram_result(result)

    def enforceMaxSMSLength(self, message):
        if len(message) > MAX_SMS_LENGTH:
            raise Exception('SMS cannot be more than ' + str(MAX_SMS_LENGTH)
                            + ' characters long!')

    def parse_hologram_result(self, response):

        # Parse int and chop of trailing zero.
        response = int(response[1])

        if response == ERR_OK:
            self.logger.info('Message received successfully')
            return errorCodeDescription[response]
        else:
            self.logger.error('Unable to receive message')

            description = errorCodeDescription[response]
            if description is not None:
                return description
            else:
                return 'Unknown error: ' + str(response)
