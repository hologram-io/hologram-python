# Cellular.py - Hologram Python SDK Cellular interface
# Author: Hologram <support@hologram.io>
#
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

from ..Event import Event
from Exceptions.HologramError import NetworkError
from Modem import Modem
from Modem import E303
from Modem import MS2131
from Modem import Nova
from Modem import NovaM_R404
from Network import Network
import subprocess
import time
import usb.core

# Cellular return codes.
CLOUD_DISCONNECTED = 0
CLOUD_CONNECTED = 1
CLOUD_ERR_SIM = 3
CLOUD_ERR_SIGNAL = 5
CLOUD_ERR_CONNECT = 12

DEFAULT_CELLULAR_TIMEOUT = 200 # slightly more than 3 mins

class Cellular(Network):

    _modemHandlers = {
        'e303': E303.E303,
        'ms2131': MS2131.MS2131,
        'nova': Nova.Nova,
        'r404': NovaM_R404.NovaM_R404,
        '': Modem
    }

    def __init__(self, event=Event()):
        super(Cellular, self).__init__(event=event)
        self._connection_status = CLOUD_DISCONNECTED
        self._modem = None

    def autodetect_modem(self):
        # scan for a modem and set it if found
        dev_devices = self._scan_for_modems()
        if dev_devices is None:
            raise NetworkError('Modem not detected')
        self.modem = dev_devices[0]


    def getConnectionStatus(self):
        return self._connection_status

    def is_connected(self):
        return self._connection_status == CLOUD_CONNECTED or self.modem.is_connected()

    def connect(self, timeout = DEFAULT_CELLULAR_TIMEOUT):
        self.logger.info('Connecting to cell network with timeout of %s seconds', timeout)
        success = False
        try:
            success = self.modem.connect(timeout = timeout)
        except KeyboardInterrupt as e:
            pass

        if success:
            self.logger.info('Successfully connected to cell network')
            # Disable at sockets mode since we're already establishing PPP.
            # This call is needed in certain modems that have limited interfaces to work with.
            self.disable_at_sockets_mode()
            self._connection_status = CLOUD_CONNECTED
            self.event.broadcast('cellular.connected')
            super(Cellular, self).connect()
        else:
            self.logger.info('Failed to connect to cell network')

        return success

    def disconnect(self):
        self.logger.info('Disconnecting from cell network')
        success = self.modem.disconnect()
        if success:
            self.logger.info('Successfully disconnected from cell network')
            self._connection_status = CLOUD_DISCONNECTED
            self.event.broadcast('cellular.disconnected')
            super(Cellular, self).connect()
        else:
            self.logger.info('Failed to disconnect from cell network')

        return success

    def reconnect(self):
        self.logger.info('Reconnecting to cell network')
        success = self.disconnect()

        if success == False:
            self.logger.info('Failed to disconnect from cell network')
            return False

        return self.connect()

    def create_socket(self):
        self.modem.create_socket()

    def connect_socket(self, host, port):
        self.modem.connect_socket(host, port)
        # This delay is required as recommended in the uBlox spec sheet.
        time.sleep(2)

    def listen_socket(self, port):
        self.modem.listen_socket(port)

    def write_socket(self, data):
        return self.modem.write_socket(data)

    def close_socket(self):
        return self.modem.close_socket()

    def send_message(self, data):
        return self.modem.send_message(data)

    def open_receive_socket(self, receive_port):
        return self.modem.open_receive_socket(receive_port)

    def pop_received_message(self):
        return self.modem.pop_received_message()

    def disable_at_sockets_mode(self):
        self.modem.disable_at_sockets_mode()

    def enableSMS(self):
        return self.modem.enableSMS()

    def disableSMS(self):
        return self.modem.disableSMS()

    def popReceivedSMS(self):
        return self.modem.popReceivedSMS()

    # EFFECTS: Returns the sim otp response from the sim.
    def get_sim_otp_response(self, command):
        return self.modem.get_sim_otp_response(command)


    def _scan_for_modems(self):
        res = None
        for (modemName, modemHandler) in self._modemHandlers.iteritems():
            if self._scan_for_modem(modemHandler):
                res = (modemName, modemHandler)
                break
        return res


    def _scan_for_modem(self, modemHandler):
        usb_ids = modemHandler.usb_ids
        for vid_pid in usb_ids:
            if not vid_pid:
                continue
            self.logger.debug('checking for vid_pid: %s', str(vid_pid))
            vid = int(vid_pid[0], 16)
            pid = int(vid_pid[1], 16)
            dev = usb.core.find(idVendor=vid, idProduct=pid)
            if dev:
                self.logger.info('Detected modem %s', modemHandler.__name__)
                return True
        return False




    @property
    def modem(self):
        return self._modem

    @modem.setter
    def modem(self, modem):
        if modem not in self._modemHandlers:
            raise NetworkError('Invalid modem type: %s' % modem)
        else:
            self._modem = self._modemHandlers[modem](event=self.event)

    @property
    def localIPAddress(self):
        return self.modem.localIPAddress

    @property
    def remoteIPAddress(self):
        return self.modem.remoteIPAddress

    @property
    def signal_strength(self):
        return self.modem.signal_strength

    @property
    def modem_id(self):
        return self.modem.modem_id

    @property
    def imsi(self):
        return self.modem.imsi

    @property
    def iccid(self):
        return self.modem.iccid

    @property
    def operator(self):
        return self.modem.operator

    # This property will be set to None if a modem is not physically attached.
    @property
    def active_modem_interface(self):
        return repr(self.modem)

    @property
    def description(self):
        return self.modem.description

    @property
    def location(self):
        return self.modem.location

    @property
    def at_sockets_available(self):
        return self.modem.at_sockets_available
