# -*- coding: utf-8 -*-
# Modem.py - Hologram Python SDK Modem interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

from IModem import IModem
from ModemMode import *
from UtilClasses import ModemResult
from UtilClasses import SMS
from Hologram.Event import Event
from Exceptions.HologramError import SerialError
from Exceptions.HologramError import HologramError
from Exceptions.HologramError import NetworkError

from collections import deque
import binascii
import datetime
import logging
import os
import serial
from serial.tools import list_ports
import time
from serial.serialutil import Timeout

DEFAULT_CHATSCRIPT_PATH = '/chatscripts/default-script'

class Modem(IModem):

    DEFAULT_MODEM_RESTART_TIME = 20
    DEFAULT_SERIAL_READ_SIZE = 256
    DEFAULT_SERIAL_TIMEOUT = 1
    DEFAULT_SERIAL_RETRIES = 0
    DEFAULT_SEND_TIMEOUT = 10

    _RETRY_DELAY = 0.05  # 50 millisecond delay to avoid spinning loops

    SOCKET_INIT = 0
    SOCKET_WRITE_STATE = 1
    SOCKET_RECEIVE_READ = 2
    SOCKET_SEND_READ = 3
    SOCKET_CLOSED = 4

    GSM = u"@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ ÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
    EXT = {
        0x40: u'|',
        0x14: u'^',
        0x65: u'€',
        0x28: u'{',
        0x29: u'}',
        0x3C: u'[',
        0x3D: u'~',
        0x3E: u']',
        0x2F: u'\\',
    }

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(Modem, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                    event=event)

        self.serial_port = None
        self.timeout = Modem.DEFAULT_SERIAL_TIMEOUT
        self.response = []
        self._at_sockets_available = False
        self.urc_state = Modem.SOCKET_INIT
        self._socket_receive_buffer = deque()
        self.socket_identifier = 0
        self.last_read_payload_length = 0
        self.result = ModemResult.OK
        self.debug_out = ''
        self.in_ext = False

        self._initialize_device_name(device_name)

        self._initialize_chatscript_file(chatscript_file)

        # This serial mode device name/port will always be equivalent to whatever the
        # default port is for the specific modem.
        self._mode = None
        self.initialize_serial_interface()
        self.logger.info('Instantiated a %s interface with device name of %s',
                         self.__repr__(), self.device_name)

    def isConnected(self):
        return self._mode.connected()

    def connect(self, timeout):
        if self._mode is None:
            self._mode = PPP(device_name=self.device_name,
                             all_attached_device_names=self.__detect_all_serial_ports(),
                             baud_rate=self.baud_rate,
                             chatscript_file=self.chatscript_file)
        return self._mode.connect(timeout = timeout)


    def disconnect(self):

        if self._mode is not None:
            return self._mode.disconnect()
        return None

    def _initialize_device_name(self, device_name):
        if device_name is None:
            devices = self.detect_usable_serial_port()
            if not devices:
                raise SerialError('Unable to detect a usable serial port')
            self.device_name = devices[0]

    def _initialize_chatscript_file(self, chatscript_file):
        if chatscript_file is None:
            # Get the absolute path of the chatscript file.
            self.chatscript_file = os.path.dirname(__file__) + DEFAULT_CHATSCRIPT_PATH
        else:
            self.chatscript_file = chatscript_file

        self.logger.info('chatscript file: %s', self.chatscript_file)

    def openSerialPort(self, device_name=None):

        if device_name is None:
            device_name = self.device_name

        try:
            self.serial_port = serial.Serial(device_name, baudrate=self.baud_rate,
                                             bytesize=8, parity='N', stopbits=1,
                                             timeout=self.timeout, write_timeout=1)
        except Exception as e:
            return False

        if not self.serial_port.isOpen():
            return False

        return True

    def closeSerialPort(self):

        self.__enforce_serial_port_open()

        try:
            self.serial_port.close()
        except Exception:
            self.logger.error('Failed to close serial port')

    # EFFECTS: backwards compatibility only
    def enableSMS(self):
        self.checkURC()
        ok, r = self.read("+CPMS")
        if ok == ModemResult.OK:
            try:
                numsms = int(r.lstrip('+CPMS: ').split(',')[1])
                for i in range(numsms):
                    self.event.broadcast('sms.received')
            except (IndexError, ValueError) as e:
                self.logger.error(repr(e))

    def disableSMS(self):
        self.enableSMS()

    def popReceivedSMS(self):
        self.checkURC()
        result, response = self.command("+CMGL")
        if result != ModemResult.OK: return None
        oldest = None
        oldest_index = None
        for i in range(0,len(response),2):
            current, current_index = self._parsePDU(response[i], response[i+1])
            if current is None: continue
            if oldest is None or current.timestamp < oldest.timestamp:
                self.logger.debug("Found Oldest: (%s) %s",  current_index, current.timestamp)
                oldest = current
                oldest_index = current_index
        if oldest_index is not None:
            self.set("+CMGD", str(oldest_index))
        return oldest

    def __detect_all_serial_ports(self, stop_on_first=False, include_all_ports=True):
        # figures out the serial ports associated with the modem and returns them
        device_names = []
        for usb_id in self.usb_ids:
            vid = usb_id[0]
            pid = usb_id[1]

            # The list_ports function returns devices in descending order, so reverse
            # the order here to iterate in ascending order (e.g. from /dev/xx0 to /dev/xx6)
            # since our usable serial devices usually start at 0.
            udevices = [x for x in list_ports.grep("{0}:{1}".format(vid, pid))]
            for udevice in reversed(udevices):
                if include_all_ports == False:
                    self.logger.debug('checking port %s', udevice.name)
                    port_opened = self.openSerialPort(udevice.device)
                    if not port_opened:
                        continue

                    res = self.command('', timeout=1)
                    if res[0] != ModemResult.OK:
                        continue
                    self.logger.info('found working port at %s', udevice.name)

                device_names.append(udevice.device)
                if stop_on_first:
                    break
            if stop_on_first and device_names:
                break
        return device_names

    def detect_usable_serial_port(self, stop_on_first=True):
        return self.__detect_all_serial_ports(stop_on_first=stop_on_first,
                                            include_all_ports=False)

    def initialize_serial_interface(self):
        self.openSerialPort()
        self.init_serial_commands()

    def init_serial_commands(self):
        pass

    def set_sms_configs(self):
        self.command("+CMGF", "0") #SMS PDU format
        self.command("+CNMI", "2,1") #SMS New Message Indication

    def set_timezone_configs(self):
        self.command("+CTZU", "1") #time/zone sync
        self.command("+CTZR", "1") #time/zone URC

    def set_network_registration_status(self):
        pass

    def reset(self):
        self.set('+CFUN', '16') # restart the modem

    def radio_power(self, power_mode):
        cfun_val = '1' if power_mode else '0'
        ok, r = self.command('+CFUN', cfun_val, timeout=5)
        return ok == ModemResult.OK

    def send_message(self, data, timeout=DEFAULT_SEND_TIMEOUT):

        self.urc_state = Modem.SOCKET_INIT

        self.write_socket(data)

        loop_timeout = Timeout(timeout)
        while self.urc_state != Modem.SOCKET_SEND_READ:
            self.checkURC()
            if self.urc_state != Modem.SOCKET_SEND_READ:
                if loop_timeout.expired():
                    raise SerialError('Timeout occurred waiting for message status')
                time.sleep(self._RETRY_DELAY)
            elif self.urc_state == Modem.SOCKET_CLOSED:
                return '[1,0]' #this is connection closed for hologram cloud response

        return self.read_socket()

    def pop_received_message(self):
        self.checkURC()
        data = None
        if len(self._socket_receive_buffer) > 0:
            data = self._socket_receive_buffer.popleft()
        return data

    def open_receive_socket(self, receive_port):
        self.create_socket()
        # self.receive_socket_thread()
        self.listen_socket(receive_port)

    def _read_and_append_message_receive_buffer(self, socket_identifier, payload_length):
        msg = self.read_socket(socket_identifier=socket_identifier, payload_length=payload_length)
        self._socket_receive_buffer.append(msg)
        self.close_socket(socket_identifier=socket_identifier)

    def create_socket(self):
        op = self._basic_set('+USOCR', '6', strip_val=False)
        if op is not None:
            self.socket_identifier = int(op)

    # REQUIRES: The host and port.
    # EFFECTS: Issues an AT command to connect to the specified socket identifier.
    def connect_socket(self, host, port):
        at_command_val = "%d,\"%s\",%s" % (self.socket_identifier, host, port)
        ok, _ = self.set('+USOCO', at_command_val, timeout=20)
        if ok != ModemResult.OK:
            self.logger.error('Failed to connect socket')
            raise NetworkError('Failed to connect socket')
        else:
            self.logger.info('Connect socket is successful')

    def listen_socket(self, port):

        at_command_val = "%d,%s" % (self.socket_identifier, port)
        self.listen_socket_identifier = self.socket_identifier
        ok, _ = self.set('+USOLI', at_command_val, timeout=5)
        if ok != ModemResult.OK:
            self.logger.error('Failed to listen socket')
            raise NetworkError('Failed to listen socket')

    def write_socket(self, data):

        self.enable_hex_mode()
        value = '%d,%s,\"%s\"' % (self.socket_identifier, len(data), binascii.hexlify(data))
        ok, _ = self.set('+USOWR', value, timeout=10)
        if ok != ModemResult.OK:
            self.logger.error('Failed to write to socket')
            raise NetworkError('Failed to write socket')
        self.disable_hex_mode()

    def read_socket(self, socket_identifier=None, payload_length=None):

        if socket_identifier is None:
            socket_identifier = self.socket_identifier

        if payload_length is None:
            payload_length = self.last_read_payload_length

        self.enable_hex_mode()

        resp = self._basic_set('+USORD', '%d,%d' % (socket_identifier, payload_length))
        if resp is not None:
            resp = resp.strip('"')
        resp = binascii.unhexlify(resp)

        self.disable_hex_mode()
        return resp

    def close_socket(self, socket_identifier=None):

        if socket_identifier is None:
            socket_identifier = self.socket_identifier

        ok, r = self.set('+USOCL', "%s" % socket_identifier)
        if ok != ModemResult.OK:
            self.logger.info('Failed to close socket')

    def debugwrite(self, x, hide=False):
        if not hide:
            self.debug_out += x
        self._write_to_serial_port_and_flush(x)

    def modemwrite(self, cmd, start=False, at=False, seteq=False, read=False,
                    end=False, hide=False):
        # Skip debugs for modem write commands if hidden mode is enabled.
        if start and not hide:
            self.debug_out = '['
        if at:
            self.debugwrite('AT', hide=hide)
        self.debugwrite(cmd, hide=hide)
        if seteq:
            self.debugwrite('=', hide=hide)
        if read:
            self.debugwrite('?', hide=hide)
        if end:
            if not hide:
                self.debug_out += ']'
                self.logger.debug(self.debug_out)
            self._write_to_serial_port_and_flush('\r\n')

    def checkURC(self, hide=False):
        while(True):
            response = self._readline_from_serial_port(0, hide=hide)
            if len(response) > 0 and response.startswith('+'):
                urc = response.rstrip('\r\n')
                self.handleURC(urc)
            else:
                return

    # EFFECTS: Handles URC related AT command responses.
    def handleURC(self, urc):
        self.logger.debug("URC! %s",  urc)
        self.logger.debug("handleURC state: %d",  self.urc_state)

        next_urc_state = self.urc_state

        if urc.startswith("+CMTI: "):
            self._handle_sms_receive_urc(urc)
        elif urc.startswith('+UULOC: '):
            self._handle_location_urc(urc)
        elif urc.startswith('+UUSORD: '):

            # Strip UUSORD socket identifier + payload length from the URC event.
            # Example: {+UUSORD: 0,2} -> 0 and 2
            response_list = urc.lstrip('+UUSORD: ').split(',')
            socket_identifier = int(response_list[0])
            payload_length = int(response_list[-1])

            if self.urc_state == Modem.SOCKET_RECEIVE_READ:
                self._read_and_append_message_receive_buffer(socket_identifier, payload_length)
            else:
                self.socket_identifier = socket_identifier
                self.last_read_payload_length = payload_length
                next_urc_state = Modem.SOCKET_SEND_READ
        elif urc.startswith('+UUSOLI: '):
            self._handle_listen_urc(urc)
            self.last_read_payload_length = 0
            next_urc_state = Modem.SOCKET_RECEIVE_READ
        elif urc.startswith('+UUPSDD: '):
            self.event.broadcast('cellular.forced_disconnect')
        elif urc.startswith('+UUSOCL: '):
            next_urc_state = Modem.SOCKET_CLOSED
        else:
            self.logger.debug("URC was not handled. \'%s\'",  urc)

        self.urc_state = next_urc_state


    # URC handlers


    def _handle_sms_receive_urc(self, urc):
        self.event.broadcast('sms.received')

    def _handle_location_urc(self, urc):
        raise NotImplementedError('Must instantiate the right modem type')

    def _handle_listen_urc(self, urc):
        self.event.broadcast('message.received')

    def process_response(self, cmd, timeout=None, hide=False):
        self.response = []
        while(True):
            response = self._readline_from_serial_port(timeout, hide=hide)
            if len(response) == 0:
                return ModemResult.Timeout

            response = response.rstrip('\r\n')

            if len(response) == 0:
                continue

            if response == 'ERROR':
                return ModemResult.Error

            if response.startswith('+CME ERROR:') or response.startswith('+CMS ERROR:'):
                self.response.append(response)
                return ModemResult.Error

            if response == 'OK':
                return ModemResult.OK

            if response.startswith('+'):
                if response.lower().startswith(cmd.lower() + ': '):
                    self.response.append(response)
                else:
                    self.handleURC(response)
            elif response.startswith('AT'+cmd):
                continue #echo log???
            else:
                self.response.append(response)

        return ModemResult.Timeout


    # EFFECTS: Checks for the ModemResult and returns a tuple of (ModemResult, response).
    #          The response can be a string or a list.
    def _command_result(self):
        if self.result == ModemResult.OK and len(self.response) == 1:
            return self.result, self.response[0]
        else:
            return self.result, self.response

    def __command_helper(self, cmd='', value=None, expected=None, timeout=None,
                retries=DEFAULT_SERIAL_RETRIES, seteq=False, read=False,
                prompt=None, data=None, hide=False):
        self.result = ModemResult.Timeout

        if cmd.endswith('?'):
            read = True
            if cmd.endswith('=?'):
                cmd = cmd[:-2]
                seteq = True
            else:
                cmd = cmd[:-1]

        for i in range(retries+1):
            self.checkURC(hide=hide)

            if value is None:
                self.modemwrite(cmd, start=True, at=True, read=read, end=True,
                                 seteq=seteq, hide=hide)
            elif read:
                self.result = ModemResult.Invalid
                return self._command_result()
            else:
                self.modemwrite(cmd, start=True, at=True, seteq=True, hide=hide)
                self.modemwrite(value, end=True, hide=hide)

            if not (prompt is None or data is None):

                p = self._read_from_serial_port(timeout, len(prompt) + 3)

                if prompt in p:
                    time.sleep(1)
                    self._write_to_serial_port_and_flush(data)

            self.result = self.process_response(cmd, timeout, hide=hide)
            if self.result == ModemResult.OK:
                if expected is not None:
                    self.result = ModemResult.NoMatch
                    for s in self.response:
                        if s.startswith(expected):
                            self.result = ModemResult.OK
                            break
                break
        return self._command_result()


    # ['+CMGL: 2,1,,26', '0791447779071413040C9144977304250500007160421062944008D4F29C0E8AC966'])
    def _parsePDU(self, header, pdu):
        try:
            if not header.startswith("+CMGL: "):
                return None, None

            index, stat, alpha, length = header[7:].split(',')

            # parse PDU
            smsc_len = int(pdu[0:2], 16)

            # smsc_number_type = int(pdu[2:4],16)
            # if smsc_number_type != 0x81 and smsc_number_type != 0x91: return (-2, hex(smsc_number_type))
            offset = smsc_len*2 + 3

            sender, offset = self._parse_sender(pdu, offset)

            if pdu[offset:offset+4] != '0000':
                return None, None

            offset += 4

            timestamp, offset = self._parse_timestamp(pdu, offset)
            message, offset = self._parse_message(pdu, offset)

            return SMS(sender, timestamp, message), index

        except ValueError as e:
            self.logger.error(repr(e))

        return None, None


    # EFFECTS: Parses the rest of the sms pdu (sender).
    def _parse_sender(self, pdu, offset):

        sms_deliver = int(pdu[offset],16)
        if sms_deliver & 0x03 != 0: return None
        offset += 1
        sender_len = int(pdu[offset:offset+2],16)
        offset += 2
        sender_number_type = int(pdu[offset:offset+2],16)
        offset += 2
        sender_read = sender_len
        if sender_read & 1 != 0: sender_read += 1
        sender_raw = pdu[offset:offset+sender_read]

        sender = None
        if sender_number_type & 0x50 == 0x50:
            #GSM-7
            sender = self._convert7to8bit(sender_raw, sender_len*4/7)
        else:
            sender = ''.join([ sender_raw[x:x+2][::-1] for x in range(0, len(sender_raw), 2) ])
            if sender_read & 1 != 0: sender = sender[:-1]
        offset += sender_read

        return sender, offset


    # EFFECTS: Parses the rest of of the sms pdu (timestamp).
    def _parse_timestamp(self, pdu, offset):
        timestamp_raw = pdu[offset:offset+14]
        timestamp = ''.join([ timestamp_raw[x:x+2][::-1] for x in range(0, len(timestamp_raw), 2) ])

        formatted_dt_str = self._format_datetime(timestamp[:-2])

        tz_byte = int(timestamp[-2:], 16)
        tz_bcd = ((tz_byte & 0x70) >> 4) * 10 + (tz_byte & 0x0F)

        delta = datetime.timedelta(minutes=15 * tz_bcd)

        # adjust to UTC from Service Center timestamp
        if (tz_byte & 0x80) == 0x80:
            formatted_dt_str += delta
        else:
            formatted_dt_str -= delta

        return formatted_dt_str, offset

    # EFFECTS: Parses the rest of of the sms pdu (message).
    def _parse_message(self, pdu, offset):

        offset += 14
        msg_len = int(pdu[offset:offset + 2], 16)
        offset += 2
        return self._convert7to8bit(pdu[offset:], msg_len), offset


    # EFFECTS: Takes in a datetime string, formats and returns it as specified below.
    def _format_datetime(self, date_str):
        return datetime.datetime.strptime(date_str, '%y%m%d%H%M%S')

    def _convert7to8bit(self, pdu, msg_len):
        last = 0
        current = 0
        i = 0
        msg = u''
        for count in range(msg_len):
            offset = count % 8
            last = current
            if offset < 7:
                current = int(pdu[i*2:i*2+2],16)
                i += 1
            c = (last >> (8-offset)) | (current << offset)
            msg += self._gsm7tochr(c & 0x7F)
        return msg

    def _gsm7tochr(self, c):
        if self.in_ext:
            self.in_ext = False
            if c in Modem.EXT.keys():
                return Modem.EXT[c]
        elif c == 0x1B:
            self.in_ext = True
            return u''
        elif c < len(Modem.GSM):
            return Modem.GSM[c]
        return u' '

    def is_connected(self):
        return self.is_registered()

    @staticmethod
    def _check_registered_helper(cmd, result):
        r = ''
        if isinstance(result, list):
            # If more than one response is provided, assume that only
            # the last response is of interest and that the
            # rest are uncaught URCs that we should disregard.
            if len(result) > 0:
                r = result[-1]
            else:
                raise SerialError('Internal error: input cannot be an empty list')
        else:
            r = result

        response_list = r.lstrip(cmd).lstrip(': ').split(',')

        if len(response_list) < 2:
            raise SerialError('Unable to parse registration URC response')

        regstatus = int(response_list[1])
        # 1: registered home network
        # 5: registered roaming
        return regstatus == 1 or regstatus == 5

    #EXPECTS: '+CREG', '+CGREG', or '+CEREG'
    def check_registered(self, cmd):
        ok, r = self.read(cmd)
        if ok == ModemResult.OK:
            try:
                return Modem._check_registered_helper(cmd, r)
            except (IndexError, ValueError) as e:
                self.logger.error(repr(e))
        return False

    def is_registered(self):
        pass

    def _is_pdp_context_active(self):
        if not self.is_registered():
            return False

        ok, r = self.set('+UPSND', '0,8')
        if ok == ModemResult.OK:
            try:
                pdpstatus = int(r.lstrip('UPSND: ').split(',')[2])
                # 1: PDP active
                return pdpstatus == 1
            except (IndexError, ValueError) as e:
                self.logger.error(repr(e))
        return False

    def _set_up_pdp_context(self):
        if self._is_pdp_context_active(): return True
        self.logger.info('Setting up PDP context')
        self.set('+UPSD', '0,1,\"hologram\"')
        self.set('+UPSD', '0,7,\"0.0.0.0\"')
        ok, _ = self.set('+UPSDA', '0,3', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context setup failed')
            raise NetworkError('Failed PDP context setup')
        else:
            self.logger.info('PDP context active')


    def __enforce_serial_port_open(self):
        if not (self.serial_port and self.serial_port.isOpen()):
            raise Exception('Serial port not open')

    def read(self, cmd, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES):
        return self.command(cmd, None, expected, timeout, retries, read=True)

    def set(self, cmd, value, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES,
            prompt=None, data=None):
        return self.command(cmd, value, expected, timeout, retries, prompt=prompt, data=data)

    def test(self, cmd, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES):
        return self.command(cmd, None, expected, timeout, retries, True, True)

    #returns the raw result of a command, with the 'CMD: ' prefix stripped
    def _basic_command(self, cmd, prefix=True):
        try:
            ok, r = self.command(cmd)
            if ok == ModemResult.OK:
                if prefix and r.startswith(cmd+': '):
                    return r.lstrip(cmd + ': ')
                else:
                    return r
        except AttributeError as e:
            self.logger.error(repr(e))
        return None


    def _basic_set(self, cmd, value, strip_val=True):
        try:
            ok, r = self.set(cmd, value)

            match_str = cmd + ': '
            if strip_val:
                match_str = match_str + value + ','

            if ok == ModemResult.OK and r.startswith(match_str):
                return r.lstrip(match_str)
        except AttributeError as e:
            self.logger.error(repr(e))
        return None


    def command(self, cmd='', value=None, expected=None, timeout=None,
                retries=DEFAULT_SERIAL_RETRIES, seteq=False, read=False,
                prompt=None, data=None, hide=False):
        try:
            return self.__command_helper(cmd, value, expected, timeout,
                    retries, seteq, read, prompt, data, hide)
        except serial.serialutil.SerialTimeoutException as e:
            self.logger.debug('unable to write to port')
            self.result = ModemResult.Error
        return self._command_result()


    ## THESE 3 SERIAL PORT INTERFACES ACTUALLY UTILIZE THE SERIAL PORT INSTANCE.

    # EFFECTS: This actually reads bytes from the serial port instance.
    def _readline_from_serial_port(self, timeout=None, hide=False):
        # Override set timeout with the given timeout if necessary
        if timeout is not None:
            self.serial_port.timeout = timeout
        r = self.serial_port.readline()
        if len(r) > 0 and not hide:
            self.logger.debug('{' + r.rstrip('\r\n') + '}')
        # Revert back to original default timeout
        if timeout is not None:
            self.serial_port.timeout = self.timeout
        return r

    # REQUIRES: a message string.
    # EFFECTS: Writes it to the actual serial port instance and flushes the buffer.
    def _write_to_serial_port_and_flush(self, message):
        self.serial_port.write(message.encode())
        self.serial_port.flush()

    # EFFECTS: This actually reads bytes from the serial port instance.
    def _read_from_serial_port(self, timeout=None, size=DEFAULT_SERIAL_READ_SIZE):
        if timeout is not None:
            self.serial_port.timeout = timeout
        r = self.serial_port.read(size)
        # Revert back to original default timeout
        if timeout is not None:
            self.serial_port.timeout = self.timeout
        return r

    def disable_at_sockets_mode(self):
        raise HologramError('Cannot disable AT command sockets on this Modem type')

    def enable_hex_mode(self):
        self.__set_hex_mode(1)

    def disable_hex_mode(self):
        self.__set_hex_mode(0)

    def __set_hex_mode(self, enable_hex_mode):
        self.command('+UDCONF', '1,%d' % enable_hex_mode)

    @property
    def serial_port(self):
        return self._serial_port

    @serial_port.setter
    def serial_port(self, serial_port):
        self._serial_port = serial_port

    # EFFECTS: Returns the Received Signal Strength Indication (RSSI) value of the modem
    @property
    def signal_strength(self):
        csq = self._basic_command('+CSQ')
        if csq is None:
            return '99,99'
        return csq

    @property
    def imsi(self):
        return self._basic_command('+CIMI', False)

    @property
    def modem_id(self):
        return self._basic_command('+CGMM')

    @property
    def iccid(self):
        return self._basic_command('+CCID')

    @property
    def operator(self):
        op = self._basic_set('+UDOPN','12')
        if op is not None:
            return op.strip('"')
        return op

    @property
    def location(self):
        raise NotImplementedError('This modem does not support this property')

    @property
    def mode(self):
        return self._mode

    @property
    def at_sockets_available(self):
        return self._at_sockets_available

    @property
    def modem_mode(self):
        mode_number = None
        # trim:
        # +UUSBCONF: 0,"",,"0x1102" -> 0
        # +UUSBCONF: 2,"ECM",,"0x1104" -> 2
        try:
            ok, res = self.read('+UUSBCONF')
            if ok == ModemResult.OK:
                mode_number = int(res.lstrip('+UUSBCONF: ').split(',')[0])
        except (IndexError, ValueError) as e:
            self.logger.error(repr(e))
        return mode_number

    @modem_mode.setter
    def modem_mode(self, mode):
        self.set('+UUSBCONF', str(mode))
        self.logger.info('Restarting modem')
        self.reset()
        self.logger.info('Modem restarted')
        self.closeSerialPort()
        time.sleep(Modem.DEFAULT_MODEM_RESTART_TIME)

    @property
    def localIPAddress(self):
        return self._mode.localIPAddress

    @property
    def remoteIPAddress(self):
        return self._mode.remoteIPAddress
