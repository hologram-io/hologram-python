# ISerial.py - Hologram Python SDK Modem ISerial interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
from ModemMode import ModemMode
from UtilClasses import Location
from UtilClasses import Timestamp
from UtilClasses import SMS
from UtilClasses import RWLock
from ....Event import Event
from Exceptions.HologramError import HologramError

from collections import deque
import threading
import time

DEFAULT_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
DEFAULT_SERIAL_BAUD_RATE = 9600
DEFAULT_SMS_RECEIVE_POLL_RATE = 1
MODEM_RESTART_TIME = 20

class ISerial(ModemMode):

    def __init__(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                 baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=1,
                 event=Event()):

        super(ISerial, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                      event=Event())

        # These are used for buffering received SMS messages
        self._receive_buffer_lock = threading.Lock()
        self._receive_buffer = deque()
        self._sms_listen_thread = None
        self.sms_disabled = True

        self.carrier = None
        self.serial_port = None
        self._serial_port_buffer = ''
        self._serial_port_lock = RWLock()

        self.openSerialPort(device_name=self.device_name, baud_rate=self.baud_rate,
                            timeout=timeout)

    def write(self, msg, expected_response=None):
        raise NotImplementedError('Must instantiate a Serial type')

    def openSerialPort(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                       baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=1):
        raise NotImplementedError('Must instantiate a Serial type')

    def closeSerialPort(self):
        raise NotImplementedError('Must instantiate a Serial type')

    # EFFECTS: Cuts out the response from the echoed serial output.
    # Example: 'CSQ\r\r\n+CSQ: 11,5\r\n\r\nOK\r\n' returns 11,5
    def _filter_return_values_from_at_response(self, msg, response):

        regEx = "\r\n" + msg + ': '

        if msg.startswith("+ULOC"):
            regEx = "+ULOC:"

        return response.strip('AT' + msg).strip(regEx).strip("OK\r\n")

    def _set_up_pdp_context(self):
        self.logger.info('Setting up PDP context')
        self.write('+UPSD=0,1,\"apn.konekt.io\"')
        self.write('+UPSD=0,7,\"0.0.0.0\"')
        self.write('+UPSDA=0,3')

    def _enable_sms_text_mode(self):
        self.logger.info('Enabling SMS text mode')
        self.write('+CMGF=1')
        self.write('+CNMI=2,2')

    # EFFECTS: Enables receive sms.
    def enableSMS(self):

        self._serial_port_lock.acquire()
        # SMS mode is already enabled.
        if self.sms_disabled == False:
            self._serial_port_lock.release()
            return
        self._serial_port_lock.release()

        self._enable_sms_text_mode()

        self._serial_port_lock.acquire()
        self.logger.info('Enabling SMS')
        self.sms_disabled = False
        self._serial_port_lock.release()

        # Spin a new thread for accepting incoming operations
        self._sms_listen_thread = threading.Thread(target=self._listen_to_sms_event)
        self._sms_listen_thread.daemon = True
        self._sms_listen_thread.start()

    # EFFECTS: A thread that listens on sms events and calls a separate thread
    #          to handle it. This will run until sms receive is explicitly disabled.
    def _listen_to_sms_event(self):

        expected_response = '+CMT'

        while True:
            self._serial_port_lock.reader_acquire()

            while self._serial_port_buffer.find(expected_response) == -1:

                if self.sms_disabled == True:
                    self._serial_port_lock.reader_release()
                    return

                self._serial_port_lock.reader_release()

                self._poll_and_read_from_serial_port(timeout=DEFAULT_SMS_RECEIVE_POLL_RATE)

                self._serial_port_lock.reader_acquire()

            self._serial_port_lock.reader_release()

            # Remove used AT command from the serial port buffer.
            response = self._get_at_response_from_buffer(expected_response)
            self._flush_used_response_from_serial_port_buffer(expected_response)

            # Spin a new thread to handle the current incoming operation.
            threading.Thread(target=self.__incoming_sms_thread,
                             args=[response]).start()

    def _poll_and_read_from_serial_port(self, timeout=1):

        # Wait a while before polling again.
        time.sleep(timeout)

        # Acquire the write lock and start writing to the serial port buffer.
        self._serial_port_lock.writer_acquire()
        self._serial_port_buffer += self.serial_port.read(256)
        self._serial_port_lock.writer_release()

    # REQUIRES: A SMS URC event.
    # EFFECTS: This threaded method accepts an inbound SMS,
    #          processes the SMS fields and appends
    #          it onto the receive buffer.
    #          It also broadcasts the sms.received event
    def __incoming_sms_thread(self, response_string):

        self._receive_buffer_lock.acquire()

        serial_response = self._parse_encoded_sms_response(response_string)

        self.logger.info('Received a SMS: ' + str(serial_response))

        # Append received message into receive buffer
        self._receive_buffer.append(serial_response)
        self.logger.info('Receive buffer: ' + str(self._receive_buffer))

        self._receive_buffer_lock.release()
        self.event.broadcast('sms.received')

    # EFFECTS: Process serial response and return a SMS object.
    def _parse_encoded_sms_response(self, encoded_response):
        msg = '+CMT'
        serial_response = self._filter_return_values_from_at_response(msg, encoded_response)
        response_list = serial_response.split(',')

        # Handle sender
        index = response_list[0].find(':')
        sender = response_list[0][index:].strip(': \"').strip('\"')

        message_timestamp_blob = response_list[-1].split('\r\n')

        # Handle timestamp
        timestamp_list = message_timestamp_blob[0].split(':')
        tzquarter = timestamp_list[2][2:][:-1]
        timestamp_list[2] = timestamp_list[2][:2]

        # Handle message
        message = message_timestamp_blob[-1]

        # Handle date
        date_list = response_list[-2].split('/')
        date_list[0] = date_list[0].strip('\"')

        timestamp_obj = Timestamp(year=date_list[0], month=date_list[1],
                                  day=date_list[2], hour=timestamp_list[0],
                                  minute=timestamp_list[1], second=timestamp_list[2],
                                  tzquarter=tzquarter)

        sms_obj = SMS(sender=sender, timestamp=timestamp_obj, message=message)
        return sms_obj

    # EFFECTS: Removes the used AT response from the serial port buffer.
    def _flush_used_response_from_serial_port_buffer(self, expected_response):

        self._serial_port_lock.writer_acquire()

        # LEFT SUBSTRING
        index = self._serial_port_buffer.find(expected_response)
        if index == -1:
            self._serial_port_lock.writer_release()
            raise HologramError('Internal SDK error: expected AT response not found')

        # This stores what came before it
        str_left = self._serial_port_buffer[:index]
        #print 'str_left: ' + str_left.encode('string_escape')

        # RIGHT SUBSTRING
        # Cut the substring off from the buffer by finding the 'right' position.
        # Find the first occurrence of AT+ since index.
        right = self._serial_port_buffer.find('AT', index)
        str_right = self._serial_port_buffer[right:]
        #print 'str_right: ' + str_right.encode('string_escape')

        self._serial_port_buffer = str_left + str_right

        self._serial_port_lock.writer_release()

    def _get_at_response_from_buffer(self, expected_response):

        # Remove the '+' sign from expected_response
        expected_response = expected_response[1:]

        self._serial_port_lock.reader_acquire()
        self.logger.debug('current serial port buffer: '
                          + self._serial_port_buffer.encode('string_escape'))

        # Get the response list by splitting them based on AT+ commands.
        # At any point in time, this list will look like:
        # ['', 'CSQ\r\r\n+CSQ: 11,5\r\n\r\nOK\r\n', 'CIMI\r\r\n234507095599838\r\n\r\nOK\r\n']
        response_list = self._serial_port_buffer.split('AT+')
        self.logger.debug('response_list: ' + str(response_list))

        self._serial_port_lock.reader_release()

        # Loop through encoded_responses and look for the right one to return.
        for encoded_response in response_list:
            if expected_response in encoded_response:
                return encoded_response

        return None

    # EFFECTS: Returns the receive buffer and pops the oldest element in it.
    def popReceivedSMS(self):
        self._receive_buffer_lock.acquire()

        if len(self._receive_buffer) == 0:
            data = None
        else:
            data = self._receive_buffer.popleft()

        self._receive_buffer_lock.release()
        return data

    def disableSMS(self):
        self._serial_port_lock.writer_acquire()

        self.logger.info('Disabling SMS')

        self.sms_disabled = True

        self._serial_port_lock.writer_release()

        self._sms_listen_thread.join()

        self._serial_port_lock.reader_acquire()
        self.logger.info('SMS receive disabled.')
        self._serial_port_lock.reader_release()

    def _populate_location_obj(self, response):
        response_list = response.split(',')
        self._location = Location(date=response_list[0],
                                  time=response_list[1],
                                  latitude=response_list[2],
                                  longitude=response_list[3],
                                  altitude=response_list[4],
                                  uncertainty=response_list[5])
        return self._location

    @property
    def modem_mode(self):
        # trim:
        # +UUSBCONF: 0,"",,"0x1102" -> 0
        # +UUSBCONF: 2,"ECM",,"0x1104" -> 2
        return (int)(self.write('+UUSBCONF?', '+UUSBCONF')[0])

    @modem_mode.setter
    def modem_mode(self, mode):
        self.write('+UUSBCONF=' + str(mode), '')
        self.logger.info('Restarting modem')
        self.write('+CFUN=16', '') # restart the modem
        self._serial_port_lock.writer_release()
        self.logger.info('Modem restarted')
        self.closeSerialPort()
        time.sleep(MODEM_RESTART_TIME)

    @property
    def carrier(self):
        return self._carrier

    @carrier.setter
    def carrier(self, carrier):
        self._carrier = carrier

    # EFFECTS: Returns the Received Signal Strength Indication (RSSI) value of the modem
    @property
    def signal_strength(self):
        return self.write('+CSQ')

    @property
    def imsi(self):
        return self.write('+CIMI')

    @property
    def iccid(self):
        return self.write('+CCID')

    @property
    def operator(self):
        return self.write('+UDOPN=12').strip(',')

    @property
    def location(self):
        self._set_up_pdp_context()
        response = self.write('+ULOC=2,2,0,360,10', expected_response='+UULOC')
        if response.startswith('+UULOC: '):
            response = response[8:]
        return self._populate_location_obj(response)

    @property
    def serial_port(self):
        return self._serial_port

    @serial_port.setter
    def serial_port(self, serial_port):
        self._serial_port = serial_port
