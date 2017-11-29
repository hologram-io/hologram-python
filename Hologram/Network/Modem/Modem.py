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
from UtilClasses import Location
from UtilClasses import ModemResult
from UtilClasses import SMS
from Hologram.Event import Event
from Exceptions.HologramError import SerialError
from Exceptions.HologramError import HologramError

from collections import deque
import binascii
import datetime
import logging
import os
import pyudev
import serial
import time

DEFAULT_CHATSCRIPT_PATH = '/chatscripts/default-script'

class Modem(IModem):

    DEFAULT_MODEM_RESTART_TIME = 20
    DEFAULT_SERIAL_READ_SIZE = 256
    DEFAULT_SERIAL_TIMEOUT = 1
    DEFAULT_SERIAL_RETRIES = 0

    SOCKET_INIT = 0
    SOCKET_WRITE_STATE = 1
    SOCKET_RECEIVE_READ = 2
    SOCKET_SEND_READ = 3

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(Modem, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                    event=event)

        self.carrier = None
        self.serial_port = None
        self.timeout = Modem.DEFAULT_SERIAL_TIMEOUT
        self.response = []
        self._at_sockets_available = False
        self.urc_state = Modem.SOCKET_INIT
        self.last_location = None
        self.last_send_response = None
        self._socket_receive_buffer = deque()
        self.socket_identifier = 0
        self.last_read_payload_length = 0
        self.last_sim_otp_command_response = None
        self.result = ModemResult.OK
        self.debug_out = ''
        self.gsm = u"@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ ÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
        self.in_ext = False
        self.ext = {
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

        if device_name is None:
            devices = self.detect_usable_serial_port()
            if not devices:
                raise SerialError('Unable to detect a usable serial port')
            self.device_name = devices[0]

        if chatscript_file is None:
            # Get the absolute path of the chatscript file.
            self.chatscript_file = os.path.dirname(__file__) + DEFAULT_CHATSCRIPT_PATH
        else:
            self.chatscript_file = chatscript_file

        self.logger.info('chatscript file: %s', self.chatscript_file)

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

    def populate_location_obj(self, response):
        response_list = response.split(',')
        self.last_location = Location(*response_list)
        return self.last_location

    def __detect_all_serial_ports(self, stop_on_first=False, include_all_ports=True):
        # figures out the serial ports associated with the modem and returns them
        context = pyudev.Context()
        device_names = []
        for usb_id in self.usb_ids:
            vid = usb_id[0]
            pid = usb_id[1]
            for udevice in context.list_devices(subsystem='tty', ID_BUS='usb',
                                                ID_VENDOR_ID=vid):
                # pyudev has some weird logic where you can't AND two different
                # properties together so we have to check it later
                if udevice['ID_MODEL_ID'] != pid:
                    continue
                devname = udevice['DEVNAME']

                if include_all_ports == False:
                    self.logger.debug('checking port %s', devname)
                    port_opened = self.openSerialPort(devname)
                    if not port_opened:
                        continue

                    res = self.command('', timeout=1)
                    if res[0] != ModemResult.OK:
                        continue
                    self.logger.info('found working port at %s', devname)

                device_names.append(devname)
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

    def send_message(self, data):

        self.urc_state = Modem.SOCKET_INIT

        self.write_socket(data)

        while self.urc_state != Modem.SOCKET_SEND_READ:
            self.checkURC()

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
        ok, _ = self.set('+USOCO', at_command_val, timeout=5)
        if ok != ModemResult.OK:
            self.logger.error('Failed to connect socket')
        else:
            self.logger.info('Connect socket is successful')

    def listen_socket(self, port):

        at_command_val = "%d,%s" % (self.socket_identifier, port)
        self.listen_socket_identifier = self.socket_identifier
        ok, _ = self.set('+USOLI', at_command_val, timeout=5)
        if ok != ModemResult.OK:
            self.logger.error('Failed to listen socket')

    def write_socket(self, data):

        self.enable_hex_mode()
        value = '%d,%s,\"%s\"' % (self.socket_identifier, len(data), binascii.hexlify(data))
        ok, _ = self.set('+USOWR', value)
        if ok != ModemResult.OK:
            self.logger.error('Failed to write to socket')
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
        self.write(x)

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
                self.logger.debug(self.debug_out + ']')
            self.write('\r\n')

    def checkURC(self, hide=False):
        while(True):
            response = self.readline(0, hide=hide)
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
        else:
            self.logger.debug("URC was not handled. \'%s\'",  urc)

        self.urc_state = next_urc_state

    def _handle_sms_receive_urc(self, urc):
        self.event.broadcast('sms.received')

    def _handle_location_urc(self, urc):
        self.populate_location_obj(urc.lstrip('+UULOC: '))
        self.event.broadcast('location.received')

    def _handle_listen_urc(self, urc):
        self.event.broadcast('message.received')

    def process_response(self, cmd, timeout=None, hide=False):
        self.response = []
        while(True):
            response = self.readline(timeout, hide=hide)
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


    def __command_result(self):
        if self.result == ModemResult.OK:
            if len(self.response) == 1:
                return ModemResult.OK, self.response[0]
            else:
                return ModemResult.OK, self.response
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
                return self.__command_result()
            else:
                self.modemwrite(cmd, start=True, at=True, seteq=True, hide=hide)
                self.modemwrite(value, end=True, hide=hide)

            if prompt is not None and data is not None:

                p = self._read(timeout, len(prompt) + 3)

                if prompt in p:
                    time.sleep(1)
                    self.write(data)

            self.result = self.process_response(cmd, timeout, hide=hide)
            if self.result == ModemResult.OK:
                if expected is not None:
                    self.result = ModemResult.NoMatch
                    for s in self.response:
                        if s.startswith(expected):
                            self.result = ModemResult.OK
                            break
                break
        return self.__command_result()

    def _gsm7tochr(self, c):
        if self.in_ext:
            self.in_ext = False
            if c in self.ext.keys():
                return self.ext[c]
        elif c == 0x1B:
            self.in_ext = True
            return u''
        elif c < len(self.gsm):
            return self.gsm[c]
        return u' '

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

    # ['+CMGL: 2,1,,26', '0791447779071413040C9144977304250500007160421062944008D4F29C0E8AC966'])
    def _parsePDU(self, header, pdu):
        try:
            if not header.startswith("+CMGL: "): return None, None
            index, stat, alpha, length = header[7:].split(',')
            #parse PDU
            smsc_len = int(pdu[0:2],16)
            # smsc_number_type = int(pdu[2:4],16)
            # if smsc_number_type != 0x81 and smsc_number_type != 0x91: return (-2, hex(smsc_number_type))
            offset = smsc_len*2 + 3
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
            if sender_number_type & 0x50 == 0x50:
                #GSM-7
                sender = self._convert7to8bit(sender_raw, sender_len*4/7)
            else:
                sender = ''.join([ sender_raw[x:x+2][::-1] for x in range(0, len(sender_raw), 2) ])
                if sender_read & 1 != 0: sender = sender[:-1]
            offset += sender_read
            if pdu[offset:offset+4] != '0000': return -4
            offset += 4
            ts_raw = pdu[offset:offset+14]
            ts = ''.join([ ts_raw[x:x+2][::-1] for x in range(0, len(ts_raw), 2) ])
            dt = datetime.datetime.strptime(ts[:-2], '%y%m%d%H%M%S')
            tz_byte = int(ts[-2:],16)
            tz_bcd = ((tz_byte & 0x70) >> 4)*10 + (tz_byte & 0x0F)
            delta = datetime.timedelta(minutes=15*tz_bcd)
            #adjust to UTC from Service Center timestamp
            if (tz_byte & 0x80) == 0x80:
                dt += delta
            else:
                dt -= delta
            offset += 14
            msg_len = int(pdu[offset:offset+2],16)
            offset += 2
            message = self._convert7to8bit(pdu[offset:], msg_len)

            return SMS(sender, dt, message), index

        except ValueError as e:
            self.logger.error(repr(e))

        return None, None

    def is_connected(self):
        return self.is_registered()

    @staticmethod
    def _check_registered_helper(cmd, result):
        r = None
        if isinstance(result, list) and len(result) > 0:
            # If more than one response is provided, assume that only
            # the last response is of interest and that the
            # rest are uncaught URCs that we should disregard.
            r = result[-1]
        else:
            r = result

        regstatus = int(r.lstrip(cmd).lstrip(': ').split(',')[1])
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
        else:
            self.logger.info('PDP context active')
        return ok == ModemResult.OK

    # EFFECTS: Parses and populates the last sim otp response.
    def parse_and_populate_last_sim_otp_response(self, response):
        self.last_sim_otp_command_response = response.split(',')[-1].strip('"')

    def __enforce_serial_port_open(self):
        if (not self.serial_port) or (not self.serial_port.isOpen()):
            raise Exception('Serial port not open')

    def read(self, cmd, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES):
        return self.command(cmd, None, expected, timeout, retries, read=True)

    def set(self, cmd, value, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES,
            prompt=None, data=None):
        return self.command(cmd, value, expected, timeout, retries, prompt=prompt, data=data)

    def test(self, cmd, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES):
        return self.command(cmd, None, expected, timeout, retries, True, True)

    def write(self, message):
        self.serial_port.write(message.encode())
        self.serial_port.flush()

    def _read(self, timeout=None, size=DEFAULT_SERIAL_READ_SIZE):
        if timeout is not None:
            self.serial_port.timeout = timeout
        r = self.serial_port.read(size)
        if timeout is not None:
            self.serial_port.timeout = timeout
        return r

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
        return self.__command_result()


    def readline(self, timeout=None, hide=False):
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
    def carrier(self):
        return self._carrier

    @carrier.setter
    def carrier(self, carrier):
        self._carrier = carrier

    @property
    def localIPAddress(self):
        return self._mode.localIPAddress

    @property
    def remoteIPAddress(self):
        return self._mode.remoteIPAddress
