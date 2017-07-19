# -*- coding: utf-8 -*-
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
from UtilClasses import SMS
from UtilClasses import ModemResult
from ....Event import Event
from Exceptions.HologramError import HologramError

import time
import datetime

class ISerial(ModemMode):

    DEFAULT_SERIAL_DEVICE_NAME = '/dev/ttyACM1'
    DEFAULT_SERIAL_BAUD_RATE = 9600
    DEFAULT_MODEM_RESTART_TIME = 20
    DEFAULT_SERIAL_READ_SIZE = 256
    DEFAULT_SERIAL_TIMEOUT = 1
    DEFAULT_SERIAL_RETRIES = 0

    def __init__(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                 baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=DEFAULT_SERIAL_TIMEOUT,
                 event=Event()):

        super(ISerial, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                      event=Event())

        self.carrier = None
        self.serial_port = None
        self.timeout = timeout
        self.response = []
        self.last_location = None
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

        if self.openSerialPort(device_name=self.device_name, baud_rate=self.baud_rate, timeout=timeout):
            self._init_modem()

    def write(self, msg, expected_response=None):
        raise NotImplementedError('Must instantiate a Serial type')

    def openSerialPort(self, device_name=DEFAULT_SERIAL_DEVICE_NAME,
                       baud_rate=DEFAULT_SERIAL_BAUD_RATE, timeout=DEFAULT_SERIAL_TIMEOUT):
        raise NotImplementedError('Must instantiate a Serial type')

    def closeSerialPort(self):
        raise NotImplementedError('Must instantiate a Serial type')

    def _write(self, message):
        raise NotImplementedError('Must instantiate a Serial type')

    def _read(self, timeout=None, size=DEFAULT_SERIAL_READ_SIZE):
        raise NotImplementedError('Must instantiate a Serial type')

    def _readline(self, timeout=None):
        raise NotImplementedError('Must instantiate a Serial type')

    def _init_modem(self):
        self.command("E0") #echo off
        self.command("+CMEE", "2") #set verbose error codes
        self.command("+CPIN?")
        self.command("+CTZU", "1") #time/zone sync
        self.command("+CTZR", "1") #time/zone URC
        #self.command("+CPIN", "") #set SIM PIN
        self.command("+CPMS", "\"ME\",\"ME\",\"ME\"")
        self.command("+CMGF", "0") #SMS PDU format
        self.command("+CNMI", "2,1") #SMS New Message Indication
        self.command("+CREG", "2")
        self.command("+CGREG", "2")

    def _handleURC(self, urc):
        self.logger.debug("URC! %s",  urc)
        if urc.startswith("+CMTI: "):
            self.event.broadcast('sms.received')
        elif urc.startswith('+UULOC: '):
            self._populate_location_obj(urc.lstrip('+UULOC: '))
            self.event.broadcast('location.received')

    def _debugwrite(self, x):
        self.debug_out += x
        self._write(x)

    def _modemwrite(self, cmd, start=False, at=False, seteq=False, read=False,
                    end=False):
        if start:
            self.debug_out = '['
        if at:
            self._debugwrite('AT')
        self._debugwrite(cmd)
        if seteq:
            self._debugwrite('=')
        if read:
            self._debugwrite('?')
        if end:
            self.logger.debug(self.debug_out + ']')
            self._write('\r\n')

    def checkURC(self):
        while(True):
            response = self._readline(0)
            if len(response) > 0 and response.startswith('+'):
                urc = response.rstrip('\r\n')
                self._handleURC(urc)
            else:
                return

    def _process_response(self, cmd, timeout=None):
        self.response = []
        while(True):
            response = self._readline(timeout)
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
                    self._handleURC(response)
            elif response.startswith('AT'+cmd):
                continue #echo log???
            else:
                self.response.append(response)

        return ModemResult.Timeout

    def read(self, cmd, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES):
        return self.command(cmd, None, expected, timeout, retries, read=True)

    def set(self, cmd, value, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES,
            prompt=None, data=None):
        return self.command(cmd, value, expected, timeout, retries, prompt=prompt, data=data)

    def test(self, cmd, expected=None, timeout=None, retries=DEFAULT_SERIAL_RETRIES):
        return self.command(cmd, None, expected, timeout, retries, True, True)

    def _commandResult(self):
        if self.result == ModemResult.OK:
            if len(self.response) == 1:
                return ModemResult.OK, self.response[0]
            else:
                return ModemResult.OK, self.response
        else:
            return self.result, self.response

    def command(self, cmd='', value=None, expected=None, timeout=None,
                retries=DEFAULT_SERIAL_RETRIES, seteq=False, read=False,
                prompt=None, data=None):
        self.result = ModemResult.Timeout

        if cmd.endswith('?'):
            read = True
            if cmd.endswith('=?'):
                cmd = cmd[:-2]
                seteq = True
            else:
                cmd = cmd[:-1]

        for i in range(retries+1):
            self.checkURC()

            if value is None:
                self._modemwrite(cmd, start=True, at=True, read=read, end=True,
                                 seteq=seteq)
            elif read:
                self.result = ModemResult.Invalid
                return self._commandResult()
            else:
                self._modemwrite(cmd, start=True, at=True, seteq=True)
                self._modemwrite(value, end=True)

            if prompt is not None and data is not None:
                p = self._read(timeout, len(prompt))
                if p == prompt:
                    self._write(data)

            self.result = self._process_response(cmd, timeout)
            if self.result == ModemResult.OK:
                if expected is not None:
                    self.result = ModemResult.NoMatch
                    for s in self.response:
                        if s.startswith(expected):
                            self.result = ModemResult.OK
                            break
                break
        return self._commandResult()

    def _gsm7tochr(self, c):
        #self.logger.debug('G: ' + hex(c) + ' ' + chr(c))
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
            delta = datetime.timedelta(minutes=15*int(ts[-2:]))
            dt += delta #UTC, adjusted for DST
            offset += 14
            msg_len = int(pdu[offset:offset+2],16)
            offset += 2
            message = self._convert7to8bit(pdu[offset:], msg_len)

            return SMS(sender, dt, message), index

        except ValueError as e:
            self.logger.error(repr(e))

        return None, None

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

    #EXPECTS: '+CREG' or '+CGREG'
    def _check_registered(self, cmd):
        ok, r = self.read(cmd)
        if ok == ModemResult.OK:
            try:
                regstatus = int(r.lstrip(cmd).lstrip(': ').split(',')[1])
                # 1: registered home network
                # 5: registered roaming
                return regstatus == 1 or regstatus == 5
            except (IndexError, ValueError) as e:
                self.logger.error(repr(e))
        return False

    def _is_registered(self):
        return self._check_registered('+CREG') or self._check_registered('+CGREG')

    def _tear_down_pdp_context(self):
        self.set('+UPSDA', '0,4')

    def _pdp_context_active(self):
        if not self._is_registered():
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
        if self._pdp_context_active(): return True
        self.logger.info('Setting up PDP context')
        self.set('+UPSD', '0,1,\"hologram\"')
        self.set('+UPSD', '0,7,\"0.0.0.0\"')
        ok, _ = self.set('+UPSDA', '0,3', timeout=30)
        if ok != ModemResult.OK:
            self.logger.error('PDP Context setup failed')
        else:
            self.logger.info('PDP context active')
        return ok == ModemResult.OK

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

    def _populate_location_obj(self, response):
        response_list = response.split(',')
        self.last_location = Location(*response_list)
        return self.last_location

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
        self.set('+CFUN', '16') # restart the modem
        self.logger.info('Modem restarted')
        self.closeSerialPort()
        time.sleep(DEFAULT_MODEM_RESTART_TIME)

    @property
    def carrier(self):
        return self._carrier

    @carrier.setter
    def carrier(self, carrier):
        self._carrier = carrier

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

    def _basic_set(self, cmd, value):
        try:
            ok, r = self.set(cmd, value)
            if ok == ModemResult.OK and r.startswith(cmd + ': ' + value + ','):
                return r.lstrip(cmd + ': ' + value + ',')
        except AttributeError as e:
            self.logger.error(repr(e))
        return None

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
        temp_loc = self.last_location
        if self._set_up_pdp_context():
            self.last_location = None
            ok, r = self.set('+ULOC', '2,2,0,10,10')
            if ok != ModemResult.OK:
                self.logger.error('Location request failed')
                return None
            while self.last_location is None and self._pdp_context_active():
                self.checkURC()
        if self.last_location is None:
            self.last_location = temp_loc
        return self.last_location
