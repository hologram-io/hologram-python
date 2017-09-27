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
from ...Event import Event
from Exceptions.HologramError import SerialError

import logging
import os
import pyudev

DEFAULT_CHATSCRIPT_PATH = '/chatscripts/default-script'

class Modem(IModem):

    def __init__(self, device_name=None, baud_rate='9600',
                 chatscript_file=None, event=Event()):

        super(Modem, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                    event=event)
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
                             all_attached_device_names=self.detect_all_serial_ports(),
                             baud_rate=self.baud_rate,
                             chatscript_file=self.chatscript_file)
        return self._mode.connect(timeout = timeout)


    def disconnect(self):
        return self._mode.disconnect()

    def enableSMS(self):
        return self._serial_mode.enableSMS()

    def disableSMS(self):
        return self._serial_mode.disableSMS()

    def popReceivedSMS(self):
        return self._serial_mode.popReceivedSMS()

    @property
    def localIPAddress(self):
        return self._mode.localIPAddress

    @property
    def remoteIPAddress(self):
        return self._mode.remoteIPAddress

    def get_sim_otp_response(self, command):
        return self._serial_mode.get_sim_otp_response(command)

    def detect_all_serial_ports(self, stop_on_first=False, include_all_ports=True):
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
                    serial = Serial(devname)
                    port_opened = serial.openSerialPort()
                    if not port_opened:
                        continue
                    res = serial.command('', timeout=1)
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
        return self.detect_all_serial_ports(stop_on_first=stop_on_first,
                                            include_all_ports=False)

    def initialize_serial_interface(self):
        self._serial_mode = Serial(device_name=self.device_name, event=self.event)
        self._serial_mode.openSerialPort()
        self._serial_mode.init_modem()

    # EFFECTS: Returns the Received Signal Strength Indication (RSSI) value of the modem
    @property
    def signal_strength(self):
        return self._serial_mode.signal_strength

    @property
    def modem_id(self):
        return self._serial_mode.modem_id

    @property
    def imsi(self):
        return self._serial_mode.imsi

    @property
    def iccid(self):
        return self._serial_mode.iccid

    @property
    def location(self):
        return self._serial_mode.location

    @property
    def operator(self):
        return self._serial_mode.operator

    @property
    def mode(self):
        return self._mode
