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
from Hologram.Network.Route import Route
from Modem import Modem
from Modem import E303
from Modem import MS2131
from Modem import Nova_U201
from Modem import NovaM
from Modem import DriverLoader
from Network import Network, NetworkScope
import time
from serial.tools import list_ports

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
        'nova': Nova_U201.Nova_U201,
        'novam': NovaM.NovaM,
        '': Modem
    }

    def __init__(self, event=Event()):
        super(Cellular, self).__init__(event=event)
        self._connection_status = CLOUD_DISCONNECTED
        self._modem = None
        self._route = Route()
        self.__receive_port = None


    def autodetect_modem(self):
        # scan for a modem and set it if found
        dev_devices = self._scan_for_modems()
        if dev_devices is None:
            raise NetworkError('Modem not detected')
        self.modem = dev_devices[0]

    def load_modem_drivers(self):
        self._load_modem_drivers()


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
            self.__configure_routing()
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
        self.__receive_port = receive_port
        self.event.subscribe('cellular.forced_disconnect', self.__reconnect_after_forced_disconnect)
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

    def __reconnect_and_receive(self):
        if not self.at_sockets_available:
            self.connect()
        self.open_receive_socket(self.__receive_port)

    def __reconnect_after_forced_disconnect(self):
        self.logger.info('Reconnecting after forced disconnect...')
        time.sleep(5)  # uBlox takes some time to update internal state after disconnect
        self.__reconnect_and_receive()
        while not self.is_connected():
            self.logger.info('Reconnect failed. Retrying in 5 seconds...')
            time.sleep(5)
            self.__reconnect_and_receive()
        self.logger.info('Ready to receive data on port %s', self.__receive_port)

    def __configure_routing(self):
        self.logger.info('Adding routes to Hologram cloud')
        self._route.add('10.176.0.0/16', self.localIPAddress)
        self._route.add('10.254.0.0/16', self.localIPAddress)
        if self.scope == NetworkScope.SYSTEM:
            self.logger.info('Adding system-wide default route to cellular interface')
            self._route.add_default(self.localIPAddress)

    def _load_modem_drivers(self):
        dl = DriverLoader.DriverLoader()
        for (modemName, modemHandler) in self._modemHandlers.iteritems():
            module = modemHandler.module
            if module:
                if not dl.is_module_loaded(module):
                    self.logger.info('Loading module %s for %s', module, modemName)
                    dl.load_module(module)
                    syspath = modemHandler.syspath
                    if syspath:
                        usb_ids = modemHandler.usb_ids
                        for vid_pid in usb_ids:
                            dl.force_driver_for_device(syspath, vid_pid[0], vid_pid[1])



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
            for dev in list_ports.grep("{0}:{1}".format(vid_pid[0], vid_pid[1])):
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
